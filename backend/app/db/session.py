from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# Create async engine. Pool configuration is adjusted if running on SQLite.
engine_args = {
    "echo": settings.DEBUG,
}
if not settings.DATABASE_URL.startswith("sqlite"):
    engine_args["pool_size"] = 20
    engine_args["max_overflow"] = 10
    engine_args["pool_pre_ping"] = True

engine = create_async_engine(settings.DATABASE_URL, **engine_args)

# Async session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection helper for getting db session."""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
