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
