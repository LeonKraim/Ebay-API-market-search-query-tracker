from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import get_settings
from app.services.ebay_finding import get_application_access_token
from app.services.ebay_sites import EBAY_SITES

_TAXONOMY_API_URL = "https://api.ebay.com/commerce/taxonomy/v1"


@dataclass
class CategorySuggestion:
    category_id: str
    category_name: str
    category_path: str


def _to_marketplace_id(site_id: str) -> str:
    return site_id.replace("-", "_")


async def _get_default_category_tree_id(
    client: httpx.AsyncClient,
    access_token: str,
    marketplace_id: str,
) -> str:
    response = await client.get(
        f"{_TAXONOMY_API_URL}/get_default_category_tree_id",
        params={"marketplace_id": marketplace_id},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response.raise_for_status()
    payload = response.json()
    return str(payload["categoryTreeId"])


def _build_category_path(entry: dict) -> str:
    ancestors = entry.get("categoryTreeNodeAncestors") or []
    names = [
        ancestor.get("categoryName")
        for ancestor in reversed(ancestors)
        if ancestor.get("categoryName")
    ]
    category = entry.get("category") or {}
    leaf_name = category.get("categoryName")
    if leaf_name:
        names.append(leaf_name)
    return " > ".join(names)


async def get_category_suggestions(site_id: str, query: str) -> list[CategorySuggestion]:
    query_text = query.strip()
    if not query_text:
        return []

    if site_id not in EBAY_SITES:
        raise ValueError(f"Unknown site_id '{site_id}'")

    settings = get_settings()
    access_token = await get_application_access_token(settings.ebay_app_id, settings.ebay_cert_id)
    marketplace_id = _to_marketplace_id(site_id)

    async with httpx.AsyncClient(timeout=settings.ebay_request_timeout_seconds) as client:
        category_tree_id = await _get_default_category_tree_id(client, access_token, marketplace_id)
        response = await client.get(
            f"{_TAXONOMY_API_URL}/category_tree/{category_tree_id}/get_category_suggestions",
            params={"q": query_text},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()

    suggestions: list[CategorySuggestion] = []
    seen_ids: set[str] = set()

    for entry in response.json().get("categorySuggestions") or []:
        category = entry.get("category") or {}
        category_id = category.get("categoryId")
        category_name = category.get("categoryName")
        if not category_id or not category_name or category_id in seen_ids:
            continue
        seen_ids.add(category_id)
        suggestions.append(
            CategorySuggestion(
                category_id=category_id,
                category_name=category_name,
                category_path=_build_category_path(entry) or category_name,
            )
        )

    return suggestions