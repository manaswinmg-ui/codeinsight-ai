import logging
from app.ai.response_parser import Finding
from app.analysis.models import StaticFinding

logger = logging.getLogger(__name__)

SEVERITY_ORDER = {
    "CRITICAL": 5,
    "HIGH": 4,
    "MEDIUM": 3,
    "LOW": 2,
    "INFO": 1,
}


class FindingMerger:
    def _static_to_finding(self, sf: StaticFinding) -> Finding:
        """Map StaticFinding to the standard Finding Pydantic model."""
        return Finding(
            title=sf.title,
            description=sf.description,
            severity=sf.severity.upper(),
            category=sf.category,
            confidence=sf.confidence,
            line_start=sf.line,
            line_end=sf.line,
            references=[f"{sf.tool} rule: {sf.rule}"] if sf.rule else None,
            suggested_fix=None,
            test_case_hint=None,
            impact=None,
            why_it_matters=None,
            improved_code=None,
            estimated_fix_time=None,
        )

    def _is_duplicate(self, f1: Finding, f2: Finding) -> bool:
        """
        Determine if two findings are duplicates.
        Rules:
        1. Same title (matching text, case-insensitive) - unless explicitly on different non-overlapping lines.
        2. Same line/overlapping range and similar description (Jaccard similarity >= 0.4).
        """
        f1_title = f1.title.strip().lower()
        f2_title = f2.title.strip().lower()
        same_title = (f1_title == f2_title)

        # Check line overlap
        lines_overlap = False
        both_have_lines = (f1.line_start is not None and f2.line_start is not None)
        if both_have_lines:
            f1_start = f1.line_start
            f1_end = f1.line_end if f1.line_end is not None else f1.line_start
            f2_start = f2.line_start
            f2_end = f2.line_end if f2.line_end is not None else f2.line_start
            
            if f1_start <= f2_end and f2_start <= f1_end:
                lines_overlap = True

        # If they have the same title, they are duplicates,
        # unless they are explicitly on different non-overlapping lines.
        if same_title and both_have_lines and not lines_overlap:
            same_title = False

        # Check description similarity
        words1 = set(f1.description.lower().split())
        words2 = set(f2.description.lower().split())
        desc_similar = False
        if words1 or words2:
            jaccard = len(words1 & words2) / len(words1 | words2)
            if jaccard >= 0.4:
                desc_similar = True

        return same_title or (lines_overlap and desc_similar)

    def _resolve_duplicate(self, f1: Finding, f2: Finding) -> Finding:
        """
        Resolve conflicts between duplicate findings.
        Returns the finding to keep (with merged line details if needed).
        Rules:
        - Keep higher confidence.
        - If confidence is equal, keep higher severity.
        - Merge line bounds from the other finding if the winner lacks them.
        """
        c1 = f1.confidence if f1.confidence is not None else 0
        c2 = f2.confidence if f2.confidence is not None else 0

        if c1 > c2:
            winner, loser = f1, f2
        elif c2 > c1:
            winner, loser = f2, f1
        else:
            s1 = SEVERITY_ORDER.get(f1.severity.upper(), 1)
            s2 = SEVERITY_ORDER.get(f2.severity.upper(), 1)
            if s1 >= s2:
                winner, loser = f1, f2
            else:
                winner, loser = f2, f1

        # Copy line numbers if winner is missing them
        if winner.line_start is None and loser.line_start is not None:
            winner.line_start = loser.line_start
        if winner.line_end is None and loser.line_end is not None:
            winner.line_end = loser.line_end

        return winner

    def merge(self, static_findings: list[StaticFinding], ai_findings: list[Finding]) -> list[Finding]:
        """Merge, deduplicate, and sort findings from static and AI pipelines."""
        all_findings = [self._static_to_finding(sf) for sf in static_findings]
        for f in ai_findings:
            f.severity = f.severity.upper()
            all_findings.append(f)

        unique_findings = []

        for curr in all_findings:
            duplicate_index = -1
            for i, uf in enumerate(unique_findings):
                if self._is_duplicate(curr, uf):
                    duplicate_index = i
                    break

            if duplicate_index == -1:
                unique_findings.append(curr)
            else:
                existing = unique_findings[duplicate_index]
                resolved = self._resolve_duplicate(existing, curr)
                unique_findings[duplicate_index] = resolved

        # Sort descending by severity
        unique_findings.sort(
            key=lambda f: SEVERITY_ORDER.get(f.severity.upper(), 1),
            reverse=True
        )

        return unique_findings
