from __future__ import annotations

import re

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from loguru import logger
from pydantic import BaseModel

from app.config import _CONFIG_PATH, get_settings
from app.routers.auth import verify_token
from app.services.ebay_taxonomy import get_category_suggestions
from app.services.ebay_sites import EBAY_SITES

router = APIRouter(prefix="/config", tags=["config"])


class CategorySuggestionRead(BaseModel):
    category_id: str
    category_name: str
    category_path: str


class CategorySuggestionList(BaseModel):
    items: list[CategorySuggestionRead]


@router.get("", dependencies=[Depends(verify_token)])
async def get_public_config():
    """Return all non-secret configuration values from config.toml."""
    logger.debug("[ROUTER] GET /config")
    settings = get_settings()
    return settings.public_config


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
async def update_settings(body: SettingsUpdate):
    """Update editable settings in config.toml."""
    text = _CONFIG_PATH.read_text(encoding="utf-8")

    if body.scheduler_default_interval_minutes is not None:
        text = re.sub(
            r'(default_interval_minutes\s*=\s*)\d+',
            rf'\g<1>{body.scheduler_default_interval_minutes}',
            text,
        )
    if body.scheduler_max_concurrent_polls is not None:
        text = re.sub(
            r'(max_concurrent_polls\s*=\s*)\d+',
            rf'\g<1>{body.scheduler_max_concurrent_polls}',
            text,
        )
    if body.ebay_max_pages is not None:
        text = re.sub(
            r'(max_pages\s*=\s*)\d+',
            rf'\g<1>{body.ebay_max_pages}',
            text,
        )
    if body.scraper_enabled is not None:
        val = "true" if body.scraper_enabled else "false"
        # Section-aware: only replace enabled inside [scraper], not [auth]
        text = re.sub(
            r'(\[scraper\][^\[]*enabled\s*=\s*)(true|false)',
            rf'\g<1>{val}',
            text,
            flags=re.DOTALL,
        )
    if body.scraper_completed_days is not None:
        text = re.sub(
            r'(completed_days\s*=\s*)\d+',
            rf'\g<1>{body.scraper_completed_days}',
            text,
        )

    _CONFIG_PATH.write_text(text, encoding="utf-8")
    logger.info("[CONFIG] Settings updated: {body}", body=body.model_dump(exclude_none=True))
    get_settings.cache_clear()
    return get_settings().public_config


@router.put("/ebay-site", dependencies=[Depends(verify_token)])
async def update_ebay_site(site_id: str = Body(..., embed=True)):
    """Update the default eBay site in config.toml and reload settings."""
    if site_id not in EBAY_SITES:
        raise HTTPException(status_code=400, detail=f"Unknown site_id '{site_id}'")

    # Read current config.toml
    text = _CONFIG_PATH.read_text(encoding="utf-8")

    # Replace site_id value in the [ebay] section
    new_text = re.sub(
        r'(site_id\s*=\s*)(".*?"|\'.*?\')',
        rf'\1"{site_id}"',
        text,
    )

    _CONFIG_PATH.write_text(new_text, encoding="utf-8")
    logger.info("[CONFIG] Updated ebay.site_id to '{site}'", site=site_id)

    # Clear cached settings so next access picks up the new value
    get_settings.cache_clear()
    settings = get_settings()

    return {"site_id": settings.ebay_site_id, "site_name": EBAY_SITES[site_id]}
