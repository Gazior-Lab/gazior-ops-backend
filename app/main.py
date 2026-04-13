from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.db.database import engine
from app.api.endpoints.v1 import auth
from app.api.endpoints.v1 import task
from app.core.exceptions import AppException

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.APP_ENV == "development":
        from app.db.init_db import init_db
        await init_db()
    yield
    await engine.dispose()

app = FastAPI(
    title="Gazior Ops API",
    version="1.0.0",
    lifespan=lifespan,
)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.message,
            "code": exc.code,
            "details": getattr(exc, "details", {}),
        },
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": str(exc.detail),
            "code": "HTTP_ERROR",
            "details": {},
        },
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An unexpected error occurred",
            "code": "INTERNAL_SERVER_ERROR",
            "details": {"error_type": exc.__class__.__name__} if settings.APP_ENV == "development" else {},
        },
    )

#  all v1 API routes

app.include_router(
    auth.router,
    prefix="/api/v1",
)
app.include_router(
    task.router,
    prefix="/api/v1",
)

@app.get('/')
def root():
    return {'message': 'Gazior Ops server is running'}
