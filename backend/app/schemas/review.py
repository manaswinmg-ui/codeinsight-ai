from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ReviewStatus


class ReviewCreate(BaseModel):
    code: str = Field(..., description="Source code to analyze")
    language: str = Field(..., description="Source code language")


class ReviewResponse(BaseModel):
    review_id: int = Field(..., description="The unique review ID")
    status: ReviewStatus = Field(..., description="Status of the review")
    created_at: datetime = Field(..., description="Timestamp of creation")

    class Config:
        from_attributes = True


class FindingResponse(BaseModel):
    id: int
    title: str = Field(..., description="Short title of the finding")
    description: str = Field(..., description="Detailed description of the issue")
    severity: str = Field(..., description="Severity level")
    status: str = Field(..., description="Current state of the finding")
    suggested_fix: str | None = Field(default=None, description="Suggested fix code snippet")
    test_case_hint: str | None = Field(default=None, description="Test case scenario")
    # Enhanced engineering metadata
    category: str | None = Field(default=None, description="Engineering category of the finding")
    confidence: int | None = Field(default=None, description="AI confidence score 0–100")
    impact: str | None = Field(default=None, description="Short description of potential impact")
    why_it_matters: str | None = Field(default=None, description="Educational explanation")
    improved_code: str | None = Field(default=None, description="Improved code snippet")
    estimated_fix_time: str | None = Field(default=None, description="Estimated time to fix")
    references: list[str] | None = Field(default=None, description="Reference links or names")
    line_start: int | None = Field(default=None, description="Start line number in source code")
    line_end: int | None = Field(default=None, description="End line number in source code")
    ticket_id: int | None = Field(default=None, description="Associated bug ticket ID")

    class Config:
        from_attributes = True


class ReviewDetailResponse(BaseModel):
    review_id: int = Field(..., alias="id")
    code: str = Field(..., description="Submitted code")
    language: str = Field(..., description="Programming language")
    status: ReviewStatus = Field(..., description="Processing status of the review")
    summary: str = Field(..., description="Dynamic quality summary")
    quality_score: int = Field(..., description="Dynamic quality score")
    findings: list[FindingResponse] = Field(default_factory=list)
    created_at: datetime = Field(..., description="Creation date")

    class Config:
        from_attributes = True
        populate_by_name = True


class ReviewListItemResponse(BaseModel):
    """Lightweight review item for history lists (no code, no findings)."""

    id: int
    language: str
    status: ReviewStatus
    created_at: datetime

    class Config:
        from_attributes = True


from typing import Generic, Literal, TypeVar

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int
    pages: int


class ReviewSearchQuery(BaseModel):
    page: int = 1
    limit: int = 10
    search: str | None = None
    status: str | None = None
    language: str | None = None
    quality_min: int | None = None
    quality_max: int | None = None
    critical_only: bool = False
    has_tickets: bool | None = None
    sort_by: Literal["newest", "oldest", "highest_quality", "lowest_quality", "most_findings", "least_findings"] = "newest"


class ReviewCompareRequest(BaseModel):
    left_review_id: int = Field(..., description="ID of the base review")
    right_review_id: int = Field(..., description="ID of the review to compare against")


class FindingComparisonItem(BaseModel):
    id: int
    title: str
    severity: str
    category: str
    line_start: int | None = None


class ReviewComparisonResponse(BaseModel):
    left_review_id: int
    right_review_id: int
    quality_difference: int
    new_findings: list[FindingComparisonItem]
    resolved_findings: list[FindingComparisonItem]
    critical_fixed_count: int
    tickets_closed_count: int

