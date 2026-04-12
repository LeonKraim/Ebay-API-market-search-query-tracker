from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from loguru import logger
from pydantic import BaseModel

from app.config import get_settings
from app.routers.auth import verify_token

router = APIRouter(prefix="/logs", tags=["logs"])

_LEVEL_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)"
    r" \| (?P<level>[A-Z]+)\s*"
    r"\| [^\|]+"
    r"\| (?P<message>.+)$"
)


class LogLine(BaseModel):
    raw: str
    timestamp: Optional[str] = None
    level: Optional[str] = None
    message: Optional[str] = None


class RecentLogsResponse(BaseModel):
    lines: list[LogLine]
    total_available: int


@router.get("/recent", response_model=RecentLogsResponse, dependencies=[Depends(verify_token)])
async def recent_logs(lines: int = Query(default=200, ge=1, le=2000)):
    """Return the last N lines of the log file as structured JSON."""
    settings = get_settings()
    log_path = Path(settings.log_file)
    if not log_path.exists():
        return RecentLogsResponse(lines=[], total_available=0)

    raw_lines: list[str] = []
    try:
        with log_path.open("r", encoding="utf-8", errors="replace") as fh:
            all_lines = fh.readlines()
        raw_lines = all_lines[-lines:]
        total = len(all_lines)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Could not read log file: {exc}") from exc

    parsed: list[LogLine] = []
    for raw in raw_lines:
        stripped = raw.rstrip("\n")
        m = _LEVEL_RE.match(stripped)
        if m:
            parsed.append(
                LogLine(
                    raw=stripped,
                    timestamp=m.group("timestamp"),
                    level=m.group("level").strip(),
                    message=m.group("message"),
                )
            )
        else:
            parsed.append(LogLine(raw=stripped))

    return RecentLogsResponse(lines=parsed, total_available=total)


@router.get("/download", dependencies=[Depends(verify_token)])
async def download_logs():
    """Stream the current log file as a plain-text download."""
    settings = get_settings()
    log_path = Path(settings.log_file)
    if not log_path.exists():
        raise HTTPException(status_code=404, detail="Log file not found yet")
    logger.info("[ROUTER] GET /logs/download — serving {path}", path=str(log_path))
    return FileResponse(
        path=str(log_path),
        media_type="text/plain",
        filename="ebay-market-intel.log",
    )
