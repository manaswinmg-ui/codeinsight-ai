from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import TicketPriority, TicketStatus


class TicketResponse(BaseModel):
    id: int
    finding_id: int
    title: str = Field(..., description="Ticket title")
    description: str = Field(..., description="Ticket description")
    priority: TicketPriority = Field(..., description="Priority level")
    status: TicketStatus = Field(..., description="Status state")
    assignee: str | None = Field(default=None, description="Assigned engineer")
    created_by: str | None = Field(default=None, description="Creator")
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = Field(default=None, description="Resolved date")
    resolution_notes: str | None = Field(default=None, description="Resolution notes")

    class Config:
        from_attributes = True


class TicketStatusUpdate(BaseModel):
    status: TicketStatus = Field(..., description="New status to transition to")
    resolution_notes: str | None = Field(
        default=None,
        description="Optional notes when resolving/closing a ticket",
    )
