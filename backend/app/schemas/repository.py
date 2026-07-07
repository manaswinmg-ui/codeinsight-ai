from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RepositoryResponse(BaseModel):
    repository_id: int = Field(..., description="Unique ID of the repository review")
    status: str = Field(..., description="Status of the repository review")
    created_at: datetime = Field(..., description="Timestamp when created")

    class Config:
        from_attributes = True


class FileReviewResponse(BaseModel):
    id: int
    file_path: str = Field(..., description="Relative file path inside ZIP")
    language: str = Field(..., description="Programming language")
    status: str = Field(..., description="Review status of individual file")
    quality_score: int = Field(..., description="Quality score 0-100")
    findings_count: int = Field(..., description="Total findings identified")
    tickets_count: int = Field(..., description="Total open bug tickets filed")

    class Config:
        from_attributes = True


class RepositoryDetailResponse(BaseModel):
    id: int
    name: str = Field(..., description="Uploaded ZIP file name")
    status: str = Field(..., description="Processing status of the repository")
    created_at: datetime
    updated_at: datetime
    language_summary: dict[str, int] = Field(default_factory=dict, description="Files per language distribution")
    overall_quality: int = Field(100, description="Overall repository quality score")
    summary: str = Field("", description="Quality summary text")

    files_analyzed: int = Field(0)
    critical_findings: int = Field(0)
    open_tickets: int = Field(0)
    duration_seconds: float | None = Field(None)

    files: list[FileReviewResponse] = Field(default_factory=list)
    largest_files: list[dict] = Field(default_factory=list)
    most_problematic_files: list[dict] = Field(default_factory=list)

    class Config:
        from_attributes = True


class RepositoryListItemResponse(BaseModel):
    id: int
    name: str
    status: str
    overall_quality: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class RepositoryQueryRequest(BaseModel):
    question: str = Field(..., description="The query about the repository content")


class RepositoryQueryResponse(BaseModel):
    answer: str = Field(..., description="Response from the model")
    model_used: str = Field(..., description="Model resolved for execution")
    cost: float = Field(..., description="Calculated API cost of operations")
    escalated: bool = Field(..., description="Whether model routing escalated")
    reason: str = Field(..., description="Reason context for model selection")
    files_retrieved: list[str] = Field(..., description="List of source files matching similarity context")


class RepositoryScanResultResponse(BaseModel):
    manifest: Any  # Reuses RepositoryManifest structure dynamically
    tree: str
    status: str
