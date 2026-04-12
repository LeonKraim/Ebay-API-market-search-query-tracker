"""
eBay Browse API client.

Uses the Browse API item_summary/search endpoint (JSON, OAuth Bearer token).
All calls are async (httpx).  Retry logic with exponential backoff is built in.
OAuth Application Access Token is obtained via client_credentials grant flow.
"""
from __future__ import annotations

import asyncio
import base64
import math
import time
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Callable

import httpx
from loguru import logger

from app.config import get_settings

_BROWSE_API_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
_OAUTH_TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
_BROWSE_SCOPE = "https://api.ebay.com/oauth/api_scope"

# Site → currency mapping for Browse API price filters
_SITE_CURRENCY: dict[str, str] = {
    "EBAY-US": "USD",
    "EBAY-GB": "GBP",
    "EBAY-DE": "EUR",
    "EBAY-AU": "AUD",
    "EBAY-CA": "CAD",
    "EBAY-FR": "EUR",
    "EBAY-IT": "EUR",
    "EBAY-ES": "EUR",
}

def _site_currency(site_id: str) -> str:
    """Map eBay site ID to currency code for price filters."""
    return _SITE_CURRENCY.get(site_id.upper(), "USD")

# Module-level token cache
_cached_token: str | None = None
_token_expires_at: float = 0.0


async def _get_access_token(app_id: str, cert_id: str) -> str:
    """Get an OAuth Application Access Token, using cache if still valid."""
    global _cached_token, _token_expires_at

    # Return cached token if still valid (with 60s safety margin)
    if _cached_token and time.time() < _token_expires_at - 60:
        return _cached_token

    credentials = base64.b64encode(f"{app_id}:{cert_id}".encode()).decode()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {credentials}",
    }
    data = {
        "grant_type": "client_credentials",
        "scope": _BROWSE_SCOPE,
    }

    logger.info("[OAUTH] Requesting new Application Access Token")
    async with httpx.AsyncClient() as client:
        response = await client.post(_OAUTH_TOKEN_URL, headers=headers, data=data, timeout=15.0)
        response.raise_for_status()

    token_data = response.json()
    _cached_token = token_data["access_token"]
    _token_expires_at = time.time() + token_data.get("expires_in", 7200)
    logger.info("[OAUTH] Token obtained, expires in {s}s", s=token_data.get("expires_in", 7200))
    return _cached_token


async def get_application_access_token(app_id: str, cert_id: str) -> str:
    """Public wrapper so other eBay services can reuse the shared OAuth token cache."""
    return await _get_access_token(app_id, cert_id)


@dataclass
class RawListing:
    item_id: str
    title: str | None = None
    gallery_url: str | None = None
    item_url: str | None = None
    current_price: Decimal | None = None
    currency: str = "GBP"
    buy_it_now: bool = False
    listing_type: str | None = None
    watch_count: int = 0
    bid_count: int = 0
    selling_state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    end_time: datetime | None = None
    description: str | None = None
    image_url: str | None = None


def _to_browse_marketplace(site_id: str) -> str:
    """Convert hyphen-format site ID (EBAY-DE) to underscore format (EBAY_DE)."""
    return site_id.replace("-", "_")


def _parse_listing(item: dict) -> RawListing:
    """Parse a Browse API itemSummary dict into a RawListing."""
    item_id = item.get("legacyItemId") or item.get("itemId") or ""

    # Price
    price_obj = item.get("price") or {}
    try:
        price = Decimal(price_obj["value"]) if "value" in price_obj else None
    except Exception:
        price = None
    currency = price_obj.get("currency", "GBP")

    # Buying options → listing_type / buy_it_now
    buying_options = item.get("buyingOptions") or []
    if "FIXED_PRICE" in buying_options:
        listing_type = "FixedPrice"
        buy_it_now = True
    elif "AUCTION" in buying_options:
        listing_type = "Auction"
        buy_it_now = False
    else:
        listing_type = buying_options[0] if buying_options else None
        buy_it_now = False

    # Bid count
    bid_count = 0
    try:
        bid_count = int(item.get("bidCount", 0))
    except (ValueError, TypeError):
        bid_count = 0

    # End time
    end_time = None
    end_str = item.get("itemEndDate")
    if end_str:
        try:
            end_time = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        except ValueError:
            end_time = None

    # Image
    image_obj = item.get("image") or {}
    image_url = image_obj.get("imageUrl")

    # Location
    location = item.get("itemLocation") or {}
    country = location.get("country")
    postal_code = location.get("postalCode")

    # URLs
    item_url = item.get("itemWebUrl")
    gallery_url = image_url  # Browse API uses the same image URL

    title = item.get("title")

    return RawListing(
        item_id=item_id,
        title=title,
        gallery_url=gallery_url,
        item_url=item_url,
        current_price=price,
        currency=currency,
        buy_it_now=buy_it_now,
        listing_type=listing_type,
        watch_count=0,
        bid_count=bid_count,
        selling_state="Active",
        country=country,
        postal_code=postal_code,
        end_time=end_time,
        image_url=image_url,
    )


async def _fetch_page(
    client: httpx.AsyncClient,
    keyword: str,
    category_id: str | None,
    site_id: str,
    page: int,
    page_size: int,
    app_id: str,
    cert_id: str,
    timeout: float,
    price_min: Decimal | None = None,
    price_max: Decimal | None = None,
) -> tuple[list[RawListing], int]:
    """Fetch a single page and return (listings, total_pages)."""
    access_token = await _get_access_token(app_id, cert_id)

    offset = (page - 1) * page_size
    params: dict[str, Any] = {
        "q": keyword,
        "limit": str(min(page_size, 200)),
        "offset": str(offset),
        "sort": "newlyListed",
    }
    if category_id:
        params["category_ids"] = category_id

    # Build filter string with buying options and optional price range
    filter_parts = ["buyingOptions:{AUCTION|FIXED_PRICE}"]
    if price_min is not None or price_max is not None:
        lo = str(price_min) if price_min is not None else ""
        hi = str(price_max) if price_max is not None else ""
        currency = _site_currency(site_id)
        filter_parts.append(f"price:[{lo}..{hi}],priceCurrency:{currency}")
    params["filter"] = ",".join(filter_parts)

    marketplace = _to_browse_marketplace(site_id)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-EBAY-C-MARKETPLACE-ID": marketplace,
        "Content-Type": "application/json",
    }

    logger.debug("[BROWSE] GET page {page} — keyword='{kw}' offset={off}", page=page, kw=keyword, off=offset)
    start = asyncio.get_event_loop().time()
    response = await client.get(_BROWSE_API_URL, params=params, headers=headers, timeout=timeout)
    elapsed_ms = int((asyncio.get_event_loop().time() - start) * 1000)

    logger.info(
        "[BROWSE] Page {page} — {status} ({ms}ms)",
        page=page, status=response.status_code, ms=elapsed_ms,
    )
    response.raise_for_status()

    data = response.json()
    items = data.get("itemSummaries") or []
    listings = [_parse_listing(i) for i in items]
    logger.info("[BROWSE] Page {page} — {n} items parsed", page=page, n=len(listings))

    # Total pages from total count
    total = data.get("total", 0)
    effective_limit = min(page_size, 200)
    total_pages = max(1, math.ceil(total / effective_limit)) if total > 0 else 0

    return listings, total_pages


async def fetch_all_listings(
    keyword: str,
    category_id: str | None = None,
    site_id: str | None = None,
    price_min: Decimal | None = None,
    price_max: Decimal | None = None,
    *,
    settings=None,
    should_cancel: Callable[[], bool] | None = None,
) -> list[RawListing]:
    """
    Fetch all pages of live listings from eBay Browse API for a keyword.
    Returns a flat list of RawListing objects.
    """
    if settings is None:
        settings = get_settings()

    site = site_id or settings.ebay_site_id
    logger.info(
        "[BROWSE] Starting fetch — keyword='{kw}' site={site} max_pages={mp}",
        kw=keyword, site=site, mp=settings.ebay_max_pages,
    )

    all_listings: list[RawListing] = []

    async with httpx.AsyncClient() as client:
        page = 1
        total_pages = 1

        while page <= min(total_pages, settings.ebay_max_pages):
            if should_cancel is not None and should_cancel():
                logger.info("[BROWSE] Cancellation requested before page {page} — stopping fetch loop", page=page)
                break

            for attempt in range(1, settings.ebay_retry_attempts + 1):
                try:
                    listings, total_pages = await _fetch_page(
                        client=client,
                        keyword=keyword,
                        category_id=category_id,
                        site_id=site,
                        page=page,
                        page_size=settings.ebay_results_per_page,
                        app_id=settings.ebay_app_id,
                        cert_id=settings.ebay_cert_id,
                        timeout=settings.ebay_request_timeout_seconds,
                        price_min=price_min,
                        price_max=price_max,
                    )
                    all_listings.extend(listings)
                    break
                except httpx.HTTPStatusError as exc:
                    if should_cancel is not None and should_cancel():
                        logger.info(
                            "[BROWSE] Cancellation requested during page {page} retry handling — stopping fetch loop",
                            page=page,
                        )
                        return all_listings
                    if exc.response.status_code == 429:
                        wait = settings.ebay_retry_backoff_seconds * (2 ** (attempt - 1))
                        logger.warning(
                            "[EBAY] Rate limited (429) — retry {a}/{m} in {w}s",
                            a=attempt, m=settings.ebay_retry_attempts, w=wait,
                        )
                        await asyncio.sleep(wait)
                    elif exc.response.status_code >= 500:
                        wait = settings.ebay_retry_backoff_seconds * (2 ** (attempt - 1))
                        logger.warning(
                            "[EBAY] Server error {code} — retry {a}/{m} in {w}s",
                            code=exc.response.status_code, a=attempt,
                            m=settings.ebay_retry_attempts, w=wait,
                        )
                        await asyncio.sleep(wait)
                    else:
                        logger.error("[EBAY] HTTP error {code} — not retrying", code=exc.response.status_code)
                        raise
                    if attempt == settings.ebay_retry_attempts:
                        logger.error("[EBAY] All retries exhausted for page {page}", page=page)
                        raise
                except httpx.TimeoutException:
                    if should_cancel is not None and should_cancel():
                        logger.info(
                            "[BROWSE] Cancellation requested during timeout retry handling on page {page} — stopping fetch loop",
                            page=page,
                        )
                        return all_listings
                    wait = settings.ebay_retry_backoff_seconds * (2 ** (attempt - 1))
                    logger.warning("[EBAY] Timeout on page {page} — retry {a}/{m}", page=page, a=attempt, m=settings.ebay_retry_attempts)
                    await asyncio.sleep(wait)
                    if attempt == settings.ebay_retry_attempts:
                        raise

            page += 1

    logger.info("[BROWSE] Fetch complete — {n} total items across {p} pages", n=len(all_listings), p=page - 1)
    return all_listings
