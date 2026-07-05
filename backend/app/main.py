from fastapi import FastAPI

from app.api.v1 import api_router
from app.config import settings
from app.middleware import LoggingMiddleware, setup_cors

app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade AI code review platform backend.",
    version="1.0.0",
    debug=settings.DEBUG,
)

# Setup CORS middleware
setup_cors(app)

# Add custom request logging middleware
app.add_middleware(LoggingMiddleware)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root() -> dict:
    """Root endpoint welcoming users and providing api configuration state."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": "1.0.0",
        "environment": settings.ENV,
        "docs_url": "/docs",
    }
