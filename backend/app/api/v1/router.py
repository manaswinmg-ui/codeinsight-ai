from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.repository import router as repository_router
from app.api.v1.endpoints.review import router as review_router
from app.api.v1.endpoints.ticket import router as ticket_router

api_router = APIRouter()

# Register endpoints
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(review_router, prefix="/reviews", tags=["reviews"])
api_router.include_router(ticket_router)
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(
    repository_router, prefix="/repositories", tags=["repositories"]
)
