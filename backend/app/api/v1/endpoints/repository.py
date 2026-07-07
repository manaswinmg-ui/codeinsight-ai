import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.repository_analysis_service import (
    RepositoryAnalysisService,
    repository_analysis_service,
)
from app.auth.dependencies import get_optional_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.repository import (
    RepositoryDetailResponse,
    RepositoryListItemResponse,
    RepositoryResponse,
    RepositoryQueryRequest,
    RepositoryQueryResponse,
    RepositoryScanResultResponse,
)

router = APIRouter()
logger = logging.getLogger("app.api.repository")


@router.post(
    "",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a repository ZIP archive for multi-file analysis",
)
async def upload_repository(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
    app_service: RepositoryAnalysisService = Depends(lambda: repository_analysis_service),
) -> RepositoryResponse:
    """
    Accepts a ZIP archive containing project source files, scans and validates limits,
    creates PENDING reviews in the database, and schedules parallel background analysis.
    """
    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a ZIP archive (.zip)."
        )

    try:
        file_bytes = await file.read()
        return await app_service.submit_repository(
            db,
            name=file.filename,
            file_bytes=file_bytes,
            background_tasks=background_tasks,
            user_id=current_user.id if current_user else None,
        )
    except ValueError as val_err:
        logger.warning(f"Validation failed during repository upload: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as err:
        logger.error(f"Unexpected error uploading repository: {err}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process repository archive."
        )


@router.post(
    "/upload",
    response_model=RepositoryScanResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Scan a repository ZIP archive and return metadata and tree without persistence",
)
async def scan_repository_upload(
    file: UploadFile,
) -> RepositoryScanResultResponse:
    """
    Accepts a ZIP archive containing project source files, runs the modular scanner synchronously,
    and returns the scan result including the manifest, ASCII tree, and statistics.
    No database persistence or AI analysis occurs.
    """
    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a ZIP archive (.zip)."
        )

    try:
        from app.repository.sources.zip_source import ZipRepositorySource
        from app.repository.repository_scanner import RepositoryScanner

        file_bytes = await file.read()
        source = ZipRepositorySource(file_bytes, file.filename)
        scan_result = RepositoryScanner.scan(source)

        return RepositoryScanResultResponse(
            manifest=scan_result.manifest,
            tree=scan_result.tree,
            status=scan_result.status
        )
    except ValueError as val_err:
        logger.warning(f"Validation failed during repository scan: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as err:
        logger.error(f"Unexpected error scanning repository: {err}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to scan repository archive."
        )


@router.get(
    "/{id}",
    response_model=RepositoryDetailResponse,
    summary="Get repository analysis details and aggregated metrics",
)
async def get_repository_detail(
    id: int,
    db: AsyncSession = Depends(get_db),
    app_service: RepositoryAnalysisService = Depends(lambda: repository_analysis_service),
) -> RepositoryDetailResponse:
    """
    Retrieve repository-level metrics, summary, quality scores, and constituent file reviews.
    """
    try:
        repo_detail = await app_service.get_repository_detail(db, id)
        if not repo_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository review with ID {id} not found."
            )
        return repo_detail
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Unexpected error fetching repository detail for ID {id}: {err}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve repository analysis details."
        )


@router.get(
    "",
    summary="List past repository reviews with pagination",
)
async def list_repositories(
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    app_service: RepositoryAnalysisService = Depends(lambda: repository_analysis_service),
) -> dict:
    """
    Retrieve a paginated list of all past repository analyses.
    """
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 10

    try:
        skip = (page - 1) * limit
        items, total = await app_service.list_repositories(db, skip=skip, limit=limit)

        pages = (total + limit - 1) // limit

        return {
            "items": [
                RepositoryListItemResponse(
                    id=repo.id,
                    name=repo.name,
                    status=repo.status,
                    overall_quality=repo.overall_quality,
                    created_at=repo.created_at
                )
                for repo in items
            ],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages
        }
    except Exception as err:
        logger.error(f"Unexpected error listing repositories: {err}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list repository logs."
        )


@router.post(
    "/{id}/query",
    response_model=RepositoryQueryResponse,
    summary="Ask a question about the repository using context-aware similarity search",
)
async def query_repository(
    id: int,
    payload: RepositoryQueryRequest,
    db: AsyncSession = Depends(get_db),
) -> RepositoryQueryResponse:
    """
    Given a repository ID and user query, perform embedding-based context retrieval
    and call the cost-optimized AI routing layer.
    """
    from app.ai.router import AIRouter
    from app.models.repository import Repository
    from sqlalchemy import select

    # Verify repository exists
    repo_result = await db.execute(select(Repository).filter(Repository.id == id))
    repo = repo_result.scalars().first()
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository review with ID {id} not found."
        )

    try:
        router_instance = AIRouter()
        result = await router_instance.query_repository(db, id, payload.question)
        return RepositoryQueryResponse(
            answer=result["answer"],
            model_used=result["model_used"],
            cost=result["cost"],
            escalated=result["escalated"],
            reason=result["reason"],
            files_retrieved=result["files_retrieved"]
        )
    except Exception as err:
        logger.error(f"Error querying repository {id}: {err}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run query on repository."
        )
