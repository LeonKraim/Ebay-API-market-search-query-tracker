"""
Async SQLAlchemy database setup.

Usage:
    from app.database import get_session, create_all_tables

    async with get_session() as session:
        result = await session.execute(select(MyModel))
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


_engine: create_async_engine | None = None  # type: ignore[type-arg]
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        logger.info(
            "[DB] Creating async engine — host={host} db={db} pool_size={ps}",
            host=settings.db_host,
            db=settings.db_name,
            ps=settings.db_pool_size,
        )
        _engine = create_async_engine(
            settings.database_url,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_pool_max_overflow,
            pool_pre_ping=True,
            echo=settings.app_debug,
        )
    return _engine


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=_get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional async session, rolled back on error."""
    factory = _get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Depends() injectable — yields a session per request."""
    async with get_session() as session:
        yield session


async def create_all_tables() -> None:
    """Create all tables that don't exist yet (used in tests and first-run)."""
    from app.models import Base as ModelsBase  # noqa: F401 — ensure models are imported
    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(ModelsBase.metadata.create_all)
    logger.info("[DB] All tables verified / created")


async def dispose_engine() -> None:
    """Release all DB connections — call during app shutdown."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        logger.info("[DB] Engine disposed")
        _engine = None
