from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db

router = APIRouter()


@router.get("", status_code=200)
async def health_check(db: AsyncSession = Depends(get_db)) -> dict:
    """Check backend and database connectivity status."""
    db_status = "healthy"
    try:
        # Perform quick select 1 to verify database responsiveness
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "services": "healthy",
    }
