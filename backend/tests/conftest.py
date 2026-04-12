"""Shared pytest fixtures for the entire test suite.

Uses an in-memory SQLite database via aiosqlite so tests need no external
Postgres instance.  The schema is created fresh for each test function.
"""
from __future__ import annotations

import sys
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# ── Make sure the backend root is on sys.path ─────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Force test env vars before importing app code
os.environ.setdefault("TESTING", "true")
os.environ.setdefault("EBAY_APP_ID", "fake-app-id")
os.environ.setdefault("EBAY_CERT_ID", "fake-cert-id")
os.environ.setdefault("DATABASE_USER", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("API_TOKEN", "test-secret")

from app.models import Base
from app.database import get_db
from app.scheduler import stop_scheduler


# ── Database fixtures ──────────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="function")
async def engine():
    """In-memory SQLite async engine — recreated per test."""
    eng = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean AsyncSession for unit tests."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session


# ── HTTP client fixture ────────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="function")
async def client(engine) -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient wired to the FastAPI app with the test DB."""
    from app.main import create_app
    from app.config import get_settings

    application = create_app()

    # Override get_db to use test engine
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    application.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(autouse=True)
async def reset_scheduler_state() -> AsyncGenerator[None, None]:
    await stop_scheduler()
    yield
    await stop_scheduler()


# ── Auth fixtures ──────────────────────────────────────────────────────────

@pytest.fixture()
def auth_headers() -> dict[str, str]:
    """Bearer token for protected endpoints (matches API_TOKEN env var)."""
    return {"Authorization": "Bearer test-secret"}


@pytest.fixture()
def no_auth_headers() -> dict[str, str]:
    return {}


# ── Sample data fixtures ───────────────────────────────────────────────────

@pytest.fixture()
def sample_query_payload() -> dict:
    return {
        "name": "Test Nintendo Switch",
        "keyword": "nintendo switch",
        "site_id": "EBAY-GB",
        "interval_minutes": 60,
        "enabled": True,
        "include_sold": False,
    }


@pytest.fixture()
def sample_query_payload_minimal() -> dict:
    return {"keyword": "ps5"}
