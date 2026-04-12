"""
Logging setup using Loguru.

Call configure_logging() once at application startup.  After that, any module
can do:

    from loguru import logger
    logger.info("[POLL] Starting snapshot #{id} ...", id=snap_id)

Both sinks are configured:
  - Colourised stdout for interactive debugging
  - Single rotating file at the path in config  (logs/app.log by default)
"""
from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from app.config import get_settings

_CONSOLE_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "{message}"
)

_FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | "
    "{name}:{function}:{line} | "
    "{message}"
)


def configure_logging() -> None:
    """Remove default handler and add our stdout + file sinks."""
    settings = get_settings()

    # Remove Loguru's default stderr handler
    logger.remove()

    # ── Colourised stdout ────────────────────────────────────────────────────
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format=_CONSOLE_FORMAT,
        colorize=True,
        enqueue=True,   # thread-safe
    )

    # ── Rotating file ────────────────────────────────────────────────────────
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        str(log_path),
        level=settings.log_level,
        format=_FILE_FORMAT,
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        encoding="utf-8",
        enqueue=True,
    )

    logger.info("[LOGGING] Logging configured — level={level}, file={file}",
                level=settings.log_level, file=settings.log_file)
