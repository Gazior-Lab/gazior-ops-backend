from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.db.database import engine
from app.api.endpoints.v1 import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────
    # Development only: auto-create tables
    if settings.APP_ENV == "development": 
        from app.db.init_db import init_db
        await init_db()
    yield
    # ── Shutdown ─────────────────────────────────────
    await engine.dispose()

app = FastAPI(
    title="Gazior Ops API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(
    auth.router,
    prefix="/api/v1",
)

@app.get('/')
def root():
    return {'message': 'Gazior Ops server is running'}


