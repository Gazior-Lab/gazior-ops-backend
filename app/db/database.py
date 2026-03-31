from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# Translate SQLAlchemy URL query options for asyncpg
raw_url = make_url(settings.DATABASE_URL)
connect_args = {}
if raw_url.drivername == "postgresql+asyncpg":
    query = dict(raw_url.query)
    if query.get("sslmode"):
        connect_args["ssl"] = True
        query.pop("sslmode", None)
        query.pop("channel_binding", None)
    if "ssl" in query and str(query["ssl"]).lower() in {"true", "1", "yes", "on"}:
        connect_args["ssl"] = True
        query.pop("ssl", None)
    if query != raw_url.query:
        raw_url = raw_url.set(query=query)

engine: AsyncEngine = create_async_engine(
    raw_url,
    connect_args=connect_args,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
    echo=settings.DEBUG
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass




