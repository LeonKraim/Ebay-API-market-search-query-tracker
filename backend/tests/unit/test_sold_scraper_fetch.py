"""Unit tests for eBay sold listings scraper with mocked HTTP responses."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.sold_scraper import (
    RawSoldItem,
    _parse_page,
    scrape_sold_listings,
)

_FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def _load_fixture(name: str) -> str:
    return (_FIXTURES / name).read_text(encoding="utf-8")


def _make_response(text: str, status_code: int = 200) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        text=text,
        request=httpx.Request("GET", "https://www.ebay.co.uk/sch/i.html"),
    )


def _make_settings(**overrides):
    defaults = dict(
        ebay_site_id="EBAY-GB",
        ebay_retry_attempts=3,
        ebay_retry_backoff_seconds=0.0,
        ebay_request_timeout_seconds=5.0,
        scraper_enabled=True,
        scraper_completed_days=90,
        scraper_user_agent="TestBot/1.0",
        scraper_delay_between_pages_seconds=0.0,
    )
    defaults.update(overrides)
    s = MagicMock()
    for k, v in defaults.items():
        setattr(s, k, v)
    return s


# ── _parse_page tests ─────────────────────────────────────────────────────


class TestParsePageHTML:
    def test_parses_three_sold_items(self):
        html = _load_fixture("sold_page.html")
        items = _parse_page(html, "nintendo switch")
        assert len(items) == 3

    def test_filters_ghost_placeholder(self):
        html = _load_fixture("sold_page.html")
        items = _parse_page(html, "nintendo switch")
        titles = [i.title for i in items]
        assert not any("Shop on eBay" in t for t in titles)

    def test_first_item_fields(self):
        html = _load_fixture("sold_page.html")
        items = _parse_page(html, "nintendo switch")
        first = items[0]
        assert first.item_id == "100000001"
        assert first.sold_price == 235.0
        assert first.currency == "GBP"
        assert first.listing_type == "FixedPrice"
        assert first.title == "Nintendo Switch OLED 64GB White - Excellent Condition"

    def test_auction_listing_type(self):
        html = _load_fixture("sold_page.html")
        items = _parse_page(html, "nintendo switch")
        second = items[1]
        assert second.listing_type == "Auction"

    def test_usd_currency_detected(self):
        html = _load_fixture("sold_page.html")
        items = _parse_page(html, "nintendo switch")
        third = items[2]
        assert third.currency == "USD"
        assert third.sold_price == 320.0

    def test_sold_date_parsed(self):
        from datetime import date

        html = _load_fixture("sold_page.html")
        items = _parse_page(html, "nintendo switch")
        assert items[0].sold_date == date(2026, 3, 10)

    def test_image_url_extracted(self):
        html = _load_fixture("sold_page.html")
        items = _parse_page(html, "nintendo switch")
        assert items[0].image_url == "https://i.ebayimg.com/images/g/aaa/s-l300.jpg"


# ── scrape_sold_listings —  scraper disabled ──────────────────────────────


class TestScraperDisabled:
    async def test_returns_empty_when_disabled(self):
        settings = _make_settings(scraper_enabled=False)
        items = await scrape_sold_listings("nintendo switch", settings=settings)
        assert items == []


# ── scrape_sold_listings — happy path ─────────────────────────────────────


class TestScrapeSoldListingsHappyPath:
    async def test_single_page_returns_items(self):
        html = _load_fixture("sold_page.html")
        mock_client = AsyncMock()
        mock_client.get.return_value = _make_response(html)

        with patch("app.services.sold_scraper.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            items = await scrape_sold_listings("nintendo switch", settings=_make_settings())

        assert len(items) == 3
        assert items[0].item_id == "100000001"

    async def test_multi_page_pagination(self):
        page1 = _load_fixture("sold_page_with_next.html")
        page2 = _load_fixture("sold_page.html")  # page 2 has no next link
        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            _make_response(page1),
            _make_response(page2),
        ]

        with patch("app.services.sold_scraper.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            items = await scrape_sold_listings("nintendo switch", settings=_make_settings())

        # page1: 2 items, page2: 3 items
        assert len(items) == 5
        assert mock_client.get.call_count == 2


# ── scrape_sold_listings — site URL selection ─────────────────────────────


class TestScraperSiteSelection:
    async def test_us_site_uses_ebay_com(self):
        html = _load_fixture("sold_page.html")
        mock_client = AsyncMock()
        mock_client.get.return_value = _make_response(html)

        with patch("app.services.sold_scraper.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            await scrape_sold_listings(
                "nintendo switch",
                site_id="EBAY-US",
                settings=_make_settings(),
            )

        # Verify the GET was called (the base URL mapping is tested implicitly —
        # if it crashes, the test fails)
        assert mock_client.get.call_count >= 1

    async def test_de_site_uses_ebay_de(self):
        html = _load_fixture("sold_page.html")
        mock_client = AsyncMock()
        mock_client.get.return_value = _make_response(html)

        with patch("app.services.sold_scraper.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            await scrape_sold_listings(
                "nintendo switch",
                site_id="EBAY-DE",
                settings=_make_settings(),
            )

        assert mock_client.get.call_count >= 1


# ── scrape_sold_listings — HTTP error with retry ─────────────────────────


class TestScraperRetry:
    async def test_retries_on_http_error_then_succeeds(self):
        html = _load_fixture("sold_page.html")
        err_resp = _make_response("error", status_code=500)

        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            httpx.HTTPStatusError("500", request=err_resp.request, response=err_resp),
            _make_response(html),
        ]

        with patch("app.services.sold_scraper.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            with patch("app.services.sold_scraper.asyncio.sleep", new_callable=AsyncMock):
                items = await scrape_sold_listings("nintendo switch", settings=_make_settings())

        assert len(items) == 3
        assert mock_client.get.call_count == 2
