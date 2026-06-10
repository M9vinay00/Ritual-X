"""FastAPI application entrypoint for Pandit Hub."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.database import AsyncSessionLocal
from app.routers import admin_router, auth_router, pandits_router, users_router,booking_router,payment_router,rating_router
from app.schemas.common import ApiResponse
from app.utils.seed import seed_admin, seed_languages, seed_locations, seed_roles, seed_services


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Seed required reference data before the API starts serving traffic."""
    async with AsyncSessionLocal() as db:
        await seed_roles(db)
        await seed_locations(db)
        await seed_languages(db)
        await seed_services(db)
        if settings.ADMIN_SEED_ON_STARTUP and settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
            await seed_admin(db)
    yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(pandits_router)
app.include_router(users_router)
app.include_router(booking_router)
app.include_router(payment_router)
app.include_router(rating_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    """Return HTTP errors using the shared response envelope."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            success=False,
            error=exc.detail,
            message=None,
            data=None,
        ).model_dump(by_alias=True),
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(_request: Request, exc: StarletteHTTPException):
    """Return framework HTTP errors using the shared response envelope."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            success=False,
            error=exc.detail,
            message=None,
            data=None,
        ).model_dump(by_alias=True),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    """Return validation errors using the shared response envelope."""
    return JSONResponse(
        status_code=422,
        content=ApiResponse(
            success=False,
            error=exc.errors(),
            message=None,
            data=None,
        ).model_dump(by_alias=True),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(_request: Request, exc: Exception):
    """Return unexpected server errors using the shared response envelope."""
    return JSONResponse(
        status_code=500,
        content=ApiResponse(
            success=False,
            error=str(exc),
            message=None,
            data=None,
        ).model_dump(by_alias=True),
    )
