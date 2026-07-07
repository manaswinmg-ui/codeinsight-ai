import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dashboard_application_service import (
    DashboardApplicationService,
    dashboard_application_service,
)
from app.db import get_db
from app.schemas.dashboard import DashboardMetrics, ReviewSummary, TicketSummary

router = APIRouter()
logger = logging.getLogger("app.api.dashboard")


@router.get(
    "/metrics",
    response_model=DashboardMetrics,
    summary="Get aggregated engineering dashboard metrics",
)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
    app_service: DashboardApplicationService = Depends(
        lambda: dashboard_application_service
    ),
) -> DashboardMetrics:
    """Retrieve workspace overview metrics (reviews, tickets, and quality averages)."""
    try:
        return await app_service.get_dashboard_metrics(db)
    except Exception as err:
        logger.error(
            "Unexpected error fetching dashboard metrics: %s", err, exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


@router.get(
    "/recent-reviews",
    response_model=list[ReviewSummary],
    summary="Get list of recent code reviews",
)
async def get_recent_reviews(
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    app_service: DashboardApplicationService = Depends(
        lambda: dashboard_application_service
    ),
) -> list[ReviewSummary]:
    """Retrieve top recent code reviews."""
    try:
        return await app_service.get_recent_reviews(db, limit)
    except Exception as err:
        logger.error("Unexpected error fetching recent reviews: %s", err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


@router.get(
    "/recent-tickets",
    response_model=list[TicketSummary],
    summary="Get list of recent tickets",
)
async def get_recent_tickets(
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    app_service: DashboardApplicationService = Depends(
        lambda: dashboard_application_service
    ),
) -> list[TicketSummary]:
    """Retrieve top recent tickets."""
    try:
        return await app_service.get_recent_tickets(db, limit)
    except Exception as err:
        logger.error("Unexpected error fetching recent tickets: %s", err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err
