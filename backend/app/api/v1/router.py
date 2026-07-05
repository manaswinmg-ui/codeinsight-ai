from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.review import router as review_router

api_router = APIRouter()

# Register endpoints
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(review_router, prefix="/reviews", tags=["reviews"])
