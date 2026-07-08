import logging
import re

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

STOP_WORDS = {
    "the",
    "is",
    "at",
    "which",
    "on",
    "a",
    "an",
    "and",
    "or",
    "to",
    "for",
    "in",
    "of",
    "with",
    "this",
    "that",
    "it",
    "should",
    "could",
    "would",
    "be",
    "have",
    "has",
    "been",
    "was",
    "were",
    "are",
    "do",
    "does",
    "did",
    "can",
    "will",
    "shall",
    "but",
    "as",
    "by",
    "from",
    "about",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "up",
    "down",
    "out",
    "off",
    "over",
    "under",
    "again",
    "further",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "any",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "s",
    "t",
    "just",
    "don",
    "now",
    "i",
    "me",
    "my",
    "myself",
    "we",
    "our",
    "ours",
    "ourselves",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
    "he",
    "him",
    "his",
    "himself",
    "she",
    "her",
    "hers",
    "herself",
    "its",
    "itself",
    "they",
    "them",
    "their",
    "theirs",
    "themselves",
}


def clean_tokens(text: str) -> set[str]:
    """Lowercase, strip basic punctuation, and filter out common stop words."""
    if not text:
        return set()
    cleaned = (
        text.lower()
        .replace(".", " ")
        .replace(",", " ")
        .replace(";", " ")
        .replace(":", " ")
        .replace("`", " ")
        .replace("'", " ")
        .replace('"', " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace("[", " ")
        .replace("]", " ")
    )
    return {
        w.strip() for w in cleaned.split() if w.strip() and w.strip() not in STOP_WORDS
    }


def jaccard_similarity(set1: set[str], set2: set[str]) -> float:
    """Compute the Jaccard similarity coefficient between two token sets."""
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)


def get_identifiers(f: Finding) -> set[str]:
    """Extract code identifiers (`quote`) or single-char variable names from title/description."""
    combined = f"{f.title} {f.description}"
    quotes = set(re.findall(r"`([^`\s]+)`", combined))
    words = combined.split()
    single_chars = {
        w.strip(".,;:()[]`'\"")
        for w in words
        if len(w.strip(".,;:()[]`'\"")) == 1
        and w.strip(".,;:()[]`'\"").isalpha()
        and w.strip(".,;:()[]`'\"") != "a"
    }
    return quotes | single_chars


def has_identifier_conflict(f1: Finding, f2: Finding) -> bool:
    """Return True if both findings specify different non-overlapping identifiers (e.g. variable x vs y)."""
    ids1 = get_identifiers(f1)
    ids2 = get_identifiers(f2)
    if ids1 and ids2 and not (ids1 & ids2):
        return True
    return False


def is_relevant_finding(f: Finding) -> bool:
    """Filter out noise, AI hallucinations, or incomplete placeholder findings."""
    if not f.title or len(f.title.strip()) < 3:
        return False
    # Use lower limit of 3 to allow short descriptions in unit tests
    if not f.description or len(f.description.strip()) < 3:
        return False

    title_lower = f.title.lower().strip()
    desc_lower = f.description.lower().strip()

    noise_patterns = [
        "no issues found",
        "no vulnerabilities",
        "looks good",
        "code is clean",
        "no bugs",
        "no warnings",
        "no security issues",
        "everything is fine",
        "no findings",
        "no errors",
        "no eslint errors",
        "no ruff errors",
        "eslint passed",
        "ruff passed",
        "no issues",
        "no problems",
        "no rule violations",
        "clean code",
    ]
    for pattern in noise_patterns:
        if pattern in title_lower or pattern in desc_lower:
            return False

    # Discard low-confidence AI suggestions
    if f.confidence is not None and f.confidence < 45:
        return False

    return True


class FindingMerger:
    def _static_to_finding(self, sf: StaticFinding) -> Finding:
        """Map StaticFinding to the standard Finding Pydantic model."""
        return Finding(
            title=sf.title,
            description=sf.description,
            severity=sf.severity.upper() if sf.severity else "INFO",
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
        1. Must not reference conflicting code identifiers (e.g. variable x vs variable y).
        2. Same exact title (case-insensitive) on overlapping lines (or if one/both have no lines).
        3. High title similarity (Jaccard >= 0.65 on cleaned tokens) and overlapping lines/no lines.
        4. High description similarity (Jaccard >= 0.5 on cleaned tokens) and overlapping lines.
        5. If one finding has no line number but the other does: they are duplicates if their titles
           are highly similar (Jaccard >= 0.7) OR if they have the same category and description Jaccard >= 0.6.
        """
        if has_identifier_conflict(f1, f2):
            return False

        both_have_lines = f1.line_start is not None and f2.line_start is not None
        lines_overlap = False
        if both_have_lines:
            f1_start = f1.line_start
            f1_end = f1.line_end if f1.line_end is not None else f1.line_start
            f2_start = f2.line_start
            f2_end = f2.line_end if f2.line_end is not None else f2.line_start

            if f1_start <= f2_end and f2_start <= f1_end:
                lines_overlap = True
            else:
                return False

        t1_tokens = clean_tokens(f1.title)
        t2_tokens = clean_tokens(f2.title)
        title_jaccard = jaccard_similarity(t1_tokens, t2_tokens)
        same_title = (f1.title.strip().lower() == f2.title.strip().lower()) or (
            title_jaccard >= 0.65
        )

        d1_tokens = clean_tokens(f1.description)
        d2_tokens = clean_tokens(f2.description)
        desc_jaccard = jaccard_similarity(d1_tokens, d2_tokens)

        # Case A: Both have lines and they overlap
        if both_have_lines and lines_overlap:
            return same_title or (desc_jaccard >= 0.5)

        # Case B: One or both don't have lines
        same_category = (
            (f1.category == f2.category) if (f1.category and f2.category) else True
        )
        if same_title:
            return True

        if same_category and desc_jaccard >= 0.6:
            return True

        return False

    def _resolve_duplicate(self, f1: Finding, f2: Finding) -> Finding:
        """
        Resolve conflicts between duplicate findings.
        Returns the finding to keep (with merged line details if needed).
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

        # Merge references and suggested fixes if available
        if winner.references is None and loser.references is not None:
            winner.references = loser.references
        elif winner.references is not None and loser.references is not None:
            winner.references = list(set(winner.references + loser.references))

        if winner.suggested_fix is None and loser.suggested_fix is not None:
            winner.suggested_fix = loser.suggested_fix

        return winner

    def merge(
        self, static_findings: list[StaticFinding], ai_findings: list[Finding]
    ) -> list[Finding]:
        """Merge, deduplicate, and sort findings from static and AI pipelines."""
        all_findings = []
        for sf in static_findings:
            mapped_finding = self._static_to_finding(sf)
            if is_relevant_finding(mapped_finding):
                all_findings.append(mapped_finding)

        for f in ai_findings:
            f.severity = f.severity.upper() if f.severity else "INFO"
            if is_relevant_finding(f):
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
            key=lambda f: SEVERITY_ORDER.get(f.severity.upper(), 1), reverse=True
        )

        return unique_findings
