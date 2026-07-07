from datetime import datetime

from pydantic import BaseModel, Field


class DashboardMetrics(BaseModel):
    reviews_count: int = Field(..., description="Total number of reviews submitted")
    completed_reviews: int = Field(..., description="Number of successfully completed reviews")
    open_tickets: int = Field(..., description="Number of currently open/unresolved tickets")
    critical_findings: int = Field(..., description="Number of critical issues detected")
    average_quality: float = Field(..., description="Average code quality score (0-100)")
    language_distribution: dict[str, int] = Field(..., description="Count of reviews grouped by programming language")


class ReviewSummary(BaseModel):
    id: int = Field(..., description="Unique review ID")
    language: str = Field(..., description="Programming language of the review")
    status: str = Field(..., description="Processing status of the review")
    created_at: datetime = Field(..., description="Creation timestamp")
    quality_score: int = Field(..., description="Dynamic quality score calculated from findings")
    findings_count: int = Field(..., description="Total findings count")
    open_tickets_count: int = Field(..., description="Count of open tickets associated with this review")


class TicketSummary(BaseModel):
    id: int = Field(..., description="Unique ticket ID")
    priority: str = Field(..., description="Priority level of the ticket (e.g., P0, P1, P2, P3)")
    status: str = Field(..., description="Resolution status (e.g., OPEN, IN_PROGRESS, etc.)")
    title: str = Field(..., description="Title of the ticket")
    review_id: int = Field(..., description="ID of the parent review")
    created_at: datetime = Field(..., description="Ticket creation timestamp")
