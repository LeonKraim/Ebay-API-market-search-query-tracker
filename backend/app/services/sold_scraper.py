"""
eBay Completed/Sold Listings Scraper.

Scrapes eBay's completed items search pages using BeautifulSoup.
Targets the current (2024-2026) eBay HTML layout.
"""
from __future__ import annotations

import asyncio
import random
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from app.config import get_settings

# eBay completed listings search URL
_EBAY_COMPLETED_URL = "https://www.ebay.co.uk/sch/i.html"

# Rotating User-Agent pool — realistic desktop browser strings
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]

# CAPTCHA / bot-challenge detection patterns (case-insensitive)
_CAPTCHA_MARKERS = [
    "captcha",
    "robot",
    "please verify",
    "are you a human",
    "unusual traffic",
    "security measure",
    "enter the characters",
]


@dataclass
class RawSoldItem:
    item_id: str | None
    title: str | None
    sold_price: float | None
    currency: str | None
    sold_date: date | None
    listing_type: str | None
    image_url: str | None
    item_url: str | None


def _extract_item_id(url: str | None) -> str | None:
    if not url:
        return None
    match = re.search(r"/itm/(\d+)", url)
    return match.group(1) if match else None


def _parse_price(price_text: str | None) -> tuple[float | None, str | None]:
    """Return (price_float, currency_code) or (None, None) if not parseable."""
    if not price_text:
        return None, None
    text = price_text.strip()
    # Reject negative prices (invalid data — strip sign would give wrong positive value)
    if text.startswith("-"):
        return None, None
    currency = "GBP"
    if "£" in text:
        currency = "GBP"
    elif "$" in text:
        currency = "USD"
    elif "€" in text:
        currency = "EUR"
    cleaned = re.sub(r"[^\d.]", "", text.replace(",", ""))
    try:
        return float(cleaned), currency
    except ValueError:
        return None, None


def _parse_date(date_text: str | None) -> date | None:
    if not date_text or not date_text.strip():
        return None
    text = date_text.strip()
    # eBay typically shows "Sold  DD Mon YYYY" or "DD Mon YYYY"
    text = re.sub(r"^sold\s+", "", text, flags=re.IGNORECASE).strip()
    for fmt in ("%d %b %Y", "%b %d, %Y", "%d %B %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _parse_page(html: str, query_keyword: str) -> list[RawSoldItem]:
    """Parse a single eBay completed items HTML page into RawSoldItem list."""
    soup = BeautifulSoup(html, "lxml")
    results: list[RawSoldItem] = []

    # Current eBay layout (2025+): items are li.s-card elements
    items = soup.select("li.s-card")
    if not items:
        # Fallback: try legacy s-item selector
        items = soup.select("li.s-item")
        if not items:
            items = soup.select("ul.srp-results li.s-item")

    logger.debug("[SCRAPER] Found {n} raw item elements", n=len(items))

    for item in items:
        # --- Detect ghost "Shop on eBay" placeholder ---
        # New layout: check s-card__title text
        title_elem = (
            item.select_one(".s-card__title")
            or item.select_one(".s-item__title")
        )
        # Legacy layout: skip if tagblock present
        if item.select_one(".s-item__title--tagblock"):
            continue

        title = title_elem.get_text(strip=True) if title_elem else None
        if title and title.lower().startswith("shop on ebay"):
            continue

        # --- Link ---
        link_elem = (
            item.select_one("a.s-card__link")
            or item.select_one("a.s-item__link")
        )
        item_url = link_elem["href"] if link_elem and link_elem.get("href") else None
        item_id = _extract_item_id(item_url)

        # --- Price ---
        price_elem = (
            item.select_one(".s-card__price")
            or item.select_one(".s-item__price")
        )
        price_text = price_elem.get_text(strip=True) if price_elem else None
        sold_price, currency = _parse_price(price_text)

        # --- Sold date ---
        # New layout: .s-card__caption > span with "Sold  DD Mon YYYY"
        date_elem = item.select_one(".s-card__caption")
        if not date_elem:
            # Legacy layout
            date_elem = item.select_one(".s-item__ended-date") or item.select_one(".s-item__title-tag")
        sold_date = _parse_date(date_elem.get_text(strip=True) if date_elem else None)

        # --- Image ---
        img_elem = (
            item.select_one("img.s-card__image")
            or item.select_one("img.s-item__image-img")
        )
        image_url = img_elem.get("src") if img_elem else None

        # --- Listing type (auction / buy it now) ---
        listing_type = None
        type_elem = (
            item.select_one(".s-item__purchase-options-with-icon")
            or item.select_one(".s-item__detail")
        )
        # New layout: check attribute rows for listing type text
        if not type_elem:
            for row in item.select(".s-card__attribute-row"):
                text = row.get_text(strip=True).lower()
                if "auction" in text or "buy it now" in text or "best offer" in text:
                    type_elem = row
                    break
        if type_elem:
            text = type_elem.get_text(strip=True).lower()
            if "auction" in text:
                listing_type = "Auction"
            elif "buy it now" in text or "bin" in text:
                listing_type = "FixedPrice"

        results.append(RawSoldItem(
            item_id=item_id,
            title=title,
            sold_price=sold_price,
            currency=currency,
            sold_date=sold_date,
            listing_type=listing_type,
            image_url=image_url,
            item_url=item_url,
        ))

    valid = [r for r in results if r.title]
    logger.info("[SCRAPER] Page parsed — {n} valid items (of {raw} raw)", n=len(valid), raw=len(results))
    return valid


def _extract_next_page_url(html: str, current_page: int) -> bool:
    """Return True if there is a next page link."""
    soup = BeautifulSoup(html, "lxml")
    next_link = soup.select_one("a.pagination__next") or soup.select_one("[aria-label='Next page']")
    return next_link is not None


def _detect_captcha(html: str) -> bool:
    """Return True if the HTML page appears to be a CAPTCHA / bot-challenge page."""
    lower = html.lower()
    for marker in _CAPTCHA_MARKERS:
        if marker in lower:
            return True
    return False


async def scrape_sold_listings(
    keyword: str,
    site_id: str | None = None,
    *,
    settings=None,
) -> list[RawSoldItem]:
    """
    Scrape eBay completed/sold listings for a keyword.
    Returns a flat list of RawSoldItem.
    """
    if settings is None:
        settings = get_settings()

    if not settings.scraper_enabled:
        logger.info("[SCRAPER] Scraper disabled in config — skipping sold listings")
        return []

    # Determine base URL by site
    site = site_id or settings.ebay_site_id
    if "US" in site:
        base_url = "https://www.ebay.com/sch/i.html"
    elif "DE" in site:
        base_url = "https://www.ebay.de/sch/i.html"
    else:
        base_url = "https://www.ebay.co.uk/sch/i.html"

    logger.info(
        "[SCRAPER] Starting sold scrape — keyword='{kw}' site={site} days_back={d}",
        kw=keyword, site=site, d=settings.scraper_completed_days,
    )

    all_items: list[RawSoldItem] = []
    base_delay = settings.scraper_delay_between_pages_seconds

    async with httpx.AsyncClient(follow_redirects=True) as client:
        page = 1
        has_next = True

        while has_next:
            # Rotate User-Agent per request
            ua = random.choice(_USER_AGENTS)
            headers = {
                "User-Agent": ua,
                "Accept-Language": "en-GB,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }

            params = {
                "_nkw": keyword,
                "LH_Complete": "1",
                "LH_Sold": "1",
                "_pgn": str(page),
            }

            logger.debug("[SCRAPER] Fetching page {page} (UA: {ua})", page=page, ua=ua[:40])
            try:
                for attempt in range(1, settings.ebay_retry_attempts + 1):
                    try:
                        resp = await client.get(
                            base_url,
                            params=params,
                            headers=headers,
                            timeout=settings.ebay_request_timeout_seconds,
                        )
                        resp.raise_for_status()
                        break
                    except httpx.HTTPStatusError as exc:
                        wait = settings.ebay_retry_backoff_seconds * (2 ** (attempt - 1))
                        logger.warning(
                            "[SCRAPER] HTTP {code} on page {page} — retry {a}/{m} in {w}s",
                            code=exc.response.status_code, page=page,
                            a=attempt, m=settings.ebay_retry_attempts, w=wait,
                        )
                        await asyncio.sleep(wait)
                        if attempt == settings.ebay_retry_attempts:
                            raise

                # CAPTCHA detection — check before parsing
                if _detect_captcha(resp.text):
                    logger.warning(
                        "[SCRAPER] CAPTCHA/bot-challenge detected on page {page} — "
                        "aborting scrape to avoid IP escalation. "
                        "Returning {n} items collected so far.",
                        page=page, n=len(all_items),
                    )
                    break

                items = _parse_page(resp.text, keyword)

                if not items:
                    logger.warning(
                        "[SCRAPER] Zero items parsed on page {page} — eBay HTML may have changed or session blocked",
                        page=page,
                    )
                    break

                all_items.extend(items)
                has_next = _extract_next_page_url(resp.text, page)
                page += 1

                if has_next:
                    # Randomized delay: base_delay + random jitter up to base_delay
                    jitter = base_delay + random.uniform(0, base_delay)
                    await asyncio.sleep(jitter)

            except Exception as exc:
                logger.error("[SCRAPER] Fatal error on page {page}: {err}", page=page, err=str(exc))
                break

    logger.info("[SCRAPER] Scrape complete — {n} total sold items", n=len(all_items))
    return all_items
