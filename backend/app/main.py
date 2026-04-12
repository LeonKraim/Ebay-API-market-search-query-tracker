"""
FastAPI application factory.

Lifespan:
  - startup: configure logging, create DB tables, start scheduler
  - shutdown: stop scheduler, dispose DB engine
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import get_settings
from app.database import create_all_tables, dispose_engine
from app.logging_setup import configure_logging
from app.routers import (
    config_router,
    listings_router,
    logs_router,
    queries_router,
    scheduler_router,
    snapshots_router,
    sold_router,
    stats_router,
)
from app.scheduler import stop_scheduler, sync_scheduler_from_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    settings = get_settings()
    logger.info("[APP] {title} starting up", title=settings.app_title)

    await create_all_tables()
    logger.info("[APP] Database tables ready")

    await sync_scheduler_from_db()
    logger.info("[APP] Startup complete — auth_enabled={auth}", auth=settings.auth_enabled)

    yield

    logger.info("[APP] Shutting down")
    await stop_scheduler()
    await dispose_engine()
    logger.info("[APP] Shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_title,
        version="1.0.0",
        description="Self-hosted eBay market intelligence platform",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ──────────────────────────────────────────────────────────
    prefix = "/api/v1"
    app.include_router(queries_router, prefix=prefix)
    app.include_router(snapshots_router, prefix=prefix)
    app.include_router(listings_router, prefix=prefix)
    app.include_router(sold_router, prefix=prefix)
    app.include_router(stats_router, prefix=prefix)
    app.include_router(scheduler_router, prefix=prefix)
    app.include_router(config_router, prefix=prefix)
    app.include_router(logs_router, prefix=prefix)

    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok", "title": settings.app_title}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    s = get_settings()
    uvicorn.run("app.main:app", host=s.api_host, port=s.api_port, reload=s.app_debug)
