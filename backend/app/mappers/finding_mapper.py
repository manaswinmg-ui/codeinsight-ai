from app.ai.response_parser import ReviewResult
from app.models.enums import FindingCategory, FindingStatus
from app.models.finding import Finding
from app.models.review import Review


class FindingMapper:
    def map(self, review: Review, review_result: ReviewResult) -> list[Finding]:
        """Convert a ReviewResult DTO into a list of transient Finding ORM entities."""
        entities = []
        for dto in review_result.findings:
            # Normalize category to ORM enum; default to UNKNOWN
            raw_category = getattr(dto, "category", None)
            try:
                category = FindingCategory(raw_category) if raw_category else FindingCategory.UNKNOWN
            except ValueError:
                category = FindingCategory.UNKNOWN

            finding_entity = Finding(
                review_id=review.id,
                title=dto.title,
                description=dto.description,
                severity=dto.severity,
                status=FindingStatus.OPEN,
                suggested_fix=dto.suggested_fix,
                test_case_hint=dto.test_case_hint,
                category=category,
                confidence=getattr(dto, "confidence", None),
                impact=getattr(dto, "impact", None),
                why_it_matters=getattr(dto, "why_it_matters", None),
                improved_code=getattr(dto, "improved_code", None),
                estimated_fix_time=getattr(dto, "estimated_fix_time", None),
                references=getattr(dto, "references", None),
            )
            entities.append(finding_entity)
        return entities
