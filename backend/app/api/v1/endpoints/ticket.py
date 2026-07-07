import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ticket_application_service import (
    TicketApplicationService,
    ticket_application_service,
)
from app.auth.dependencies import get_optional_current_user
from app.db import get_db
from app.models.enums import TicketStatus
from app.models.user import User
from app.repositories.ticket_query_repository import ticket_query_repository
from app.schemas.review import PaginatedResponse
from app.schemas.ticket import TicketResponse, TicketStatusUpdate
from app.services.ticket_service import (
    FindingNotFoundError,
    InvalidStatusTransitionError,
    TicketAlreadyExistsError,
    TicketNotFoundError,
)

router = APIRouter()
logger = logging.getLogger("app.api.ticket")


@router.post(
    "/findings/{finding_id}/ticket",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a bug ticket from an AI finding",
)
async def create_ticket(
    finding_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
    app_service: TicketApplicationService = Depends(lambda: ticket_application_service),
) -> TicketResponse:
    """Create a bug ticket from a code review finding."""
    try:
        return await app_service.create_ticket(
            db, finding_id, user_id=current_user.id if current_user else None
        )
    except FindingNotFoundError as fnf_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(fnf_err),
        ) from fnf_err
    except TicketAlreadyExistsError as tae_err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(tae_err),
        ) from tae_err
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        ) from val_err
    except Exception as err:
        logger.error(
            "Unexpected error creating ticket for finding %d: %s",
            finding_id,
            err,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketResponse,
    summary="Get details of a bug ticket",
)
async def get_ticket_details(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    app_service: TicketApplicationService = Depends(lambda: ticket_application_service),
) -> TicketResponse:
    """Retrieve details for a specific bug ticket."""
    try:
        result = await app_service.get_ticket(db, ticket_id)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )
        return result
    except HTTPException:
        raise
    except Exception as err:
        logger.error(
            "Unexpected error retrieving ticket %d: %s",
            ticket_id,
            err,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


@router.patch(
    "/tickets/{ticket_id}/status",
    response_model=TicketResponse,
    summary="Update the status of a bug ticket",
)
async def update_ticket_status(
    ticket_id: int,
    payload: TicketStatusUpdate,
    db: AsyncSession = Depends(get_db),
    app_service: TicketApplicationService = Depends(lambda: ticket_application_service),
) -> TicketResponse:
    """Transition a ticket to a new status with validation."""
    try:
        return await app_service.update_ticket_status(
            db, ticket_id, payload.status, payload.resolution_notes
        )
    except TicketNotFoundError as tnf_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(tnf_err),
        ) from tnf_err
    except InvalidStatusTransitionError as ist_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ist_err),
        ) from ist_err
    except Exception as err:
        logger.error(
            "Unexpected error updating ticket %d status: %s",
            ticket_id,
            err,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


@router.get(
    "/tickets",
    response_model=PaginatedResponse[TicketResponse],
    summary="Get paginated list of tickets",
)
async def list_tickets(
    page: int = 1,
    limit: int = 10,
    status: TicketStatus | None = None,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[TicketResponse]:
    """Retrieve tickets with optional status filtering and pagination."""
    try:
        items, total = await ticket_query_repository.search_tickets(
            db, page, limit, status
        )
        pages = (total + limit - 1) // limit if limit > 0 else 1
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )
    except Exception as err:
        logger.error("Unexpected error in list tickets API: %s", err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err
