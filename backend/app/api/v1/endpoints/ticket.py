import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ticket_application_service import (
    TicketApplicationService,
    ticket_application_service,
)
from app.db import get_db
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
    app_service: TicketApplicationService = Depends(
        lambda: ticket_application_service
    ),
) -> TicketResponse:
    """Create a bug ticket from a code review finding."""
    try:
        return await app_service.create_ticket(db, finding_id)
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
    app_service: TicketApplicationService = Depends(
        lambda: ticket_application_service
    ),
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
    app_service: TicketApplicationService = Depends(
        lambda: ticket_application_service
    ),
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
