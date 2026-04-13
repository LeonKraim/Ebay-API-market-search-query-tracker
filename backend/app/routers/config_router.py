from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.settings import AppSetting
from app.models.query import SearchQuery
from app.routers.auth import verify_token
from app.services.ebay_taxonomy import get_category_suggestions
from app.services.ebay_sites import EBAY_SITES

router = APIRouter(prefix="/config", tags=["config"])

# Keys stored in the DB; config.toml provides the defaults.
_EDITABLE_KEYS = {
    "scheduler_default_interval_minutes",
    "scheduler_max_concurrent_polls",
    "ebay_max_pages",
    "scraper_enabled",
    "scraper_completed_days",
    "ebay_site_id",
}


async def _load_db_overrides(db: AsyncSession) -> dict[str, str]:
    result = await db.execute(select(AppSetting))
    return {row.key: row.value for row in result.scalars().all()}


async def _save_db_setting(db: AsyncSession, key: str, value: str) -> None:
    existing = await db.get(AppSetting, key)
    if existing:
        existing.value = value
    else:
        db.add(AppSetting(key=key, value=value))
    await db.commit()


def _build_public_config(overrides: dict[str, str]) -> dict:
    s = get_settings()

    def _int(key: str, default: int) -> int:
        return int(overrides[key]) if key in overrides else default

    def _bool(key: str, default: bool) -> bool:
        if key in overrides:
            val = overrides[key].lower()
            return val in ("true", "1", "yes")
        return default

    return {
        "app_title": s.app_title,
        "app_debug": s.app_debug,
        "auth_enabled": s.auth_enabled,
        "cors_origins": s.cors_origins,
        "ebay": {
            "site_id": overrides.get("ebay_site_id", s.ebay_site_id),
            "max_pages": _int("ebay_max_pages", s.ebay_max_pages),
        },
        "scheduler": {
            "default_interval_minutes": _int("scheduler_default_interval_minutes", s.scheduler_default_interval_minutes),
            "max_concurrent_polls": _int("scheduler_max_concurrent_polls", s.scheduler_max_concurrent_polls),
        },
        "scraper": {
            "enabled": _bool("scraper_enabled", s.scraper_enabled),
            "completed_days": _int("scraper_completed_days", s.scraper_completed_days),
        },
    }


class CategorySuggestionRead(BaseModel):
    category_id: str
    category_name: str
    category_path: str


class CategorySuggestionList(BaseModel):
    items: list[CategorySuggestionRead]


@router.get("", dependencies=[Depends(verify_token)])
async def get_public_config(db: AsyncSession = Depends(get_db)):
    """Return all non-secret configuration values, with DB overrides applied."""
    logger.debug("[ROUTER] GET /config")
    overrides = await _load_db_overrides(db)
    return _build_public_config(overrides)


@router.get("/ebay-sites", dependencies=[Depends(verify_token)])
async def list_ebay_sites():
    """Return all supported eBay marketplace site IDs."""
    return [{"id": sid, "name": name} for sid, name in EBAY_SITES.items()]


@router.get(
    "/ebay-category-suggestions",
    response_model=CategorySuggestionList,
    dependencies=[Depends(verify_token)],
)
async def list_ebay_category_suggestions(
    site_id: str = Query(...),
    q: str = Query(...),
):
    if site_id not in EBAY_SITES:
        raise HTTPException(status_code=400, detail=f"Unknown site_id '{site_id}'")

    query_text = q.strip()
    if not query_text:
        return CategorySuggestionList(items=[])

    logger.info("[CONFIG] Fetching category suggestions site_id='{site}' q='{query}'", site=site_id, query=query_text)
    suggestions = await get_category_suggestions(site_id, query_text)
    return CategorySuggestionList(
        items=[CategorySuggestionRead(**suggestion.__dict__) for suggestion in suggestions]
    )


class SettingsUpdate(BaseModel):
    scheduler_default_interval_minutes: int | None = None
    scheduler_max_concurrent_polls: int | None = None
    ebay_max_pages: int | None = None
    scraper_enabled: bool | None = None
    scraper_completed_days: int | None = None


@router.patch("/settings", dependencies=[Depends(verify_token)])
async def update_settings(body: SettingsUpdate, db: AsyncSession = Depends(get_db)):
    """Persist editable settings to the database so they survive redeployments."""
    patch = body.model_dump(exclude_none=True)
    for key, val in patch.items():
        await _save_db_setting(db, key, str(val).lower() if isinstance(val, bool) else str(val))
    logger.info("[CONFIG] Settings updated: {patch}", patch=patch)
    overrides = await _load_db_overrides(db)
    return _build_public_config(overrides)


@router.put("/ebay-site", dependencies=[Depends(verify_token)])
async def update_ebay_site(site_id: str = Body(..., embed=True), db: AsyncSession = Depends(get_db)):
    """Persist the default eBay site to the database."""
    if site_id not in EBAY_SITES:
        raise HTTPException(status_code=400, detail=f"Unknown site_id '{site_id}'")

    await _save_db_setting(db, "ebay_site_id", site_id)
    logger.info("[CONFIG] Updated ebay.site_id to '{site}'", site=site_id)
    return {"site_id": site_id, "site_name": EBAY_SITES[site_id]}


@router.get("/persistence-check", dependencies=[Depends(verify_token)])
async def check_persistence(db: AsyncSession = Depends(get_db)):
    """
    Diagnostic endpoint: Returns database state to verify that user settings
    persist across container restarts and deployments.
    
    If this endpoint shows an empty app_settings table after you've saved settings,
    it indicates the PostgreSQL volume is not persisting data.
    """
    from datetime import datetime
    from sqlalchemy import func
    
    # Count records in each table
    result = await db.execute(select(func.count()).select_from(AppSetting))
    setting_count = result.scalar() or 0
    
    result = await db.execute(select(func.count()).select_from(SearchQuery))
    query_count = result.scalar() or 0
    
    # Get all current settings
    result = await db.execute(select(AppSetting))
    all_settings = {row.key: row.value for row in result.scalars().all()}
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "app_settings_count": setting_count,
        "saved_queries_count": query_count,
        "settings": all_settings,
        "persistence_status": "✅ Data persisting" if setting_count > 0 else "❌ No persistent data",
    }

