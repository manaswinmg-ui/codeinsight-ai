import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.review_application_service import (
    ReviewApplicationService,
    review_application_service,
)
from app.application.review_history_application_service import (
    ReviewHistoryApplicationService,
    review_history_application_service,
)
from app.auth.dependencies import get_optional_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.dashboard import ReviewSummary
from app.schemas.review import (
    PaginatedResponse,
    ReviewCompareRequest,
    ReviewComparisonResponse,
    ReviewCreate,
    ReviewDetailResponse,
    ReviewResponse,
    ReviewSearchQuery,
)

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
    current_user: User | None = Depends(get_optional_current_user),
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
            user_id=current_user.id if current_user else None,
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
    "",
    response_model=PaginatedResponse[ReviewSummary],
    summary="Search, filter, sort, and paginate code reviews",
)
async def search_reviews(
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    status: str | None = None,
    language: str | None = None,
    quality_min: int | None = None,
    quality_max: int | None = None,
    critical_only: bool = False,
    has_tickets: bool | None = None,
    sort_by: str = "newest",
    db: AsyncSession = Depends(get_db),
    app_service: ReviewHistoryApplicationService = Depends(
        lambda: review_history_application_service
    ),
) -> PaginatedResponse[ReviewSummary]:
    """Retrieve history of reviews with global search, filters, sorting, and pagination."""
    query = ReviewSearchQuery(
        page=page,
        limit=limit,
        search=search,
        status=status,
        language=language,
        quality_min=quality_min,
        quality_max=quality_max,
        critical_only=critical_only,
        has_tickets=has_tickets,
        sort_by=sort_by,
    )
    try:
        return await app_service.search_reviews(db, query)
    except Exception as err:
        logger.error("Unexpected error in review search API: %s", err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


@router.post(
    "/compare",
    response_model=ReviewComparisonResponse,
    summary="Compare findings and quality score differences between two reviews",
)
async def compare_reviews(
    payload: ReviewCompareRequest,
    db: AsyncSession = Depends(get_db),
    app_service: ReviewHistoryApplicationService = Depends(
        lambda: review_history_application_service
    ),
) -> ReviewComparisonResponse:
    """Compare a base and target review to inspect new and resolved findings."""
    try:
        return await app_service.compare_reviews(
            db, payload.left_review_id, payload.right_review_id
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        ) from val_err
    except Exception as err:
        logger.error("Unexpected error in review comparison API: %s", err, exc_info=True)
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
