"""Alembic env.py — async SQLAlchemy migration environment."""
import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ── Alembic Config object ──────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Import metadata from our models ──────────────────────────────────────
from app.models import Base  # noqa: E402

target_metadata = Base.metadata

# ── Override sqlalchemy.url from the environment if available ─────────────
def _db_url() -> str:
    u = os.environ.get("DATABASE_URL")
    if u:
        return u
    host     = os.environ.get("DATABASE_HOST",     "localhost")
    port     = os.environ.get("DATABASE_PORT",     "5432")
    name     = os.environ.get("DATABASE_NAME",     "ebay_market_intel")
    user     = os.environ.get("DATABASE_USER",     "ebay")
    password = os.environ.get("DATABASE_PASSWORD", "change_me")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"


config.set_main_option("sqlalchemy.url", _db_url())


# ── Offline migrations ─────────────────────────────────────────────────────
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online migrations ──────────────────────────────────────────────────────
def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
