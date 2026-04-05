import app.models  # noqa: F401 — register all models on Base.metadata

from app.db.database import Base, engine


async def init_db() -> None:
    """
    Creates tables on startup — for development only.
    In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db() -> None:
    """Dispose engine connection pool on shutdown."""
    await engine.dispose()