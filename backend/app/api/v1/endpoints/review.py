import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.review_application_service import (
    ReviewApplicationService,
    review_application_service,
)
from app.db import get_db
from app.schemas.review import ReviewCreate, ReviewDetailResponse, ReviewResponse

router = APIRouter()
logger = logging.getLogger("app.api.review")


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new code review request",
)
async def create_review(
    payload: ReviewCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    app_service: ReviewApplicationService = Depends(
        lambda: review_application_service
    ),
) -> ReviewResponse:
    """Submit code and language to start a new review request in PENDING state."""
    try:
        return await app_service.submit_review(
            db,
            code=payload.code,
            language=payload.language,
            background_tasks=background_tasks,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        ) from val_err
    except Exception as err:
        logger.error(
            "Unexpected error in review creation API: %s", err, exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


@router.get(
    "/{review_id}",
    response_model=ReviewDetailResponse,
    summary="Get details of a code review including findings",
)
async def get_review_details(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    app_service: ReviewApplicationService = Depends(
        lambda: review_application_service
    ),
) -> ReviewDetailResponse:
    """Fetch review details, metrics, and findings."""
    try:
        result = await app_service.get_review_detail(db, review_id)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )
        return result
    except HTTPException:
        raise
    except Exception as err:
        logger.error(
            "Unexpected error in review retrieval API: %s", err, exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err
