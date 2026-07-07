from pydantic import BaseModel, Field


class StaticFinding(BaseModel):
    title: str = Field(..., description="Short title of the finding")
    description: str = Field(..., description="Detailed description of the issue")
    severity: str = Field(
        ..., description="Severity level: critical, high, medium, low, info"
    )
    line: int = Field(..., description="Line number where the finding occurs")
    column: int = Field(..., description="Column number where the finding starts")
    rule: str = Field(..., description="Analyzer-specific rule code (e.g., F401)")
    tool: str = Field(..., description="Name of the static analysis tool (e.g., ruff)")
    category: str = Field(
        default="UNKNOWN", description="Engineering category of the finding"
    )
    confidence: int = Field(
        default=100,
        description="Confidence score 0-100 (defaults to 100 for static tools)",
    )
