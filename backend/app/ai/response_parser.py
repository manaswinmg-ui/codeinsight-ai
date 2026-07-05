from pydantic import BaseModel, Field


class Finding(BaseModel):
    title: str = Field(..., description="Short title of the finding")
    description: str = Field(..., description="Detailed description of the issue")
    severity: str = Field(..., description="Severity level string (critical, high, medium, low, info)")
    suggested_fix: str | None = Field(
        default=None, description="Suggested code snippet fix"
    )
    test_case_hint: str | None = Field(
        default=None, description="Test case description"
    )
    # Enhanced fields
    category: str | None = Field(
        default="UNKNOWN", description="Engineering category of the finding"
    )
    confidence: int | None = Field(
        default=None, description="AI confidence score 0–100"
    )
    impact: str | None = Field(
        default=None, description="Short description of potential runtime impact"
    )
    why_it_matters: str | None = Field(
        default=None, description="Educational explanation of why this issue matters"
    )
    improved_code: str | None = Field(
        default=None, description="Optional improved code snippet without markdown fences"
    )
    estimated_fix_time: str | None = Field(
        default=None, description="Short estimate of time to fix"
    )
    references: list[str] | None = Field(
        default=None, description="Optional list of references (OWASP, PEP, docs)"
    )


class ReviewResult(BaseModel):
    summary: str = Field(..., description="Overall analysis summary")
    quality_score: int = Field(
        ..., description="Code quality rating score from 0 to 100"
    )
    findings: list[Finding] = Field(
        default_factory=list, description="List of findings"
    )


def _normalize_str(value: object, fallback: str | None = None) -> str | None:
    """Coerce a value to a stripped string, or return fallback if empty/None."""
    if value is None:
        return fallback
    s = str(value).strip()
    return s if s else fallback


def _normalize_confidence(value: object) -> int | None:
    """Coerce confidence to int in [0, 100], or None if invalid."""
    if value is None:
        return None
    try:
        c = int(value)
        return max(0, min(100, c))
    except (ValueError, TypeError):
        return None


def _normalize_category(value: object) -> str:
    """Normalize category string to uppercase, defaulting to UNKNOWN."""
    valid = {
        "BUG", "SECURITY", "PERFORMANCE", "MAINTAINABILITY",
        "READABILITY", "RELIABILITY", "BEST_PRACTICE", "DOCUMENTATION", "UNKNOWN",
    }
    if value is None:
        return "UNKNOWN"
    normalized = str(value).strip().upper()
    return normalized if normalized in valid else "UNKNOWN"


def _normalize_severity(value: object) -> str:
    """Normalize severity to a standard level. Defaults to INFO."""
    valid = {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
    # legacy aliases
    legacy = {"low": "LOW", "medium": "MEDIUM", "high": "HIGH"}
    if value is None:
        return "INFO"
    raw = str(value).strip()
    upper = raw.upper()
    if upper in valid:
        return upper
    if raw.lower() in legacy:
        return legacy[raw.lower()]
    return "INFO"


def _normalize_references(value: object) -> list[str] | None:
    """Normalize references to a list of strings, or None if not a list."""
    if value is None:
        return None
    if not isinstance(value, list):
        return None
    result = [str(r).strip() for r in value if r and str(r).strip()]
    return result if result else None


class ResponseParser:
    def parse(self, validated_response: dict) -> ReviewResult:
        """Parse validated AI response dictionary into typed ReviewResult structure."""
        raw_findings = validated_response.get("findings", [])
        parsed_findings = []

        for f in raw_findings:
            if not isinstance(f, dict):
                continue

            finding_obj = Finding(
                title=_normalize_str(f.get("title"), "") or "",
                description=_normalize_str(f.get("description"), "") or "",
                severity=_normalize_severity(f.get("severity")),
                suggested_fix=_normalize_str(f.get("suggested_fix")),
                test_case_hint=_normalize_str(f.get("test_case_hint")),
                category=_normalize_category(f.get("category")),
                confidence=_normalize_confidence(f.get("confidence")),
                impact=_normalize_str(f.get("impact")),
                why_it_matters=_normalize_str(f.get("why_it_matters")),
                improved_code=_normalize_str(f.get("improved_code")),
                estimated_fix_time=_normalize_str(f.get("estimated_fix_time")),
                references=_normalize_references(f.get("references")),
            )
            parsed_findings.append(finding_obj)

        return ReviewResult(
            summary=str(validated_response.get("summary", "")).strip(),
            quality_score=int(validated_response.get("quality_score", 0)),
            findings=parsed_findings,
        )

