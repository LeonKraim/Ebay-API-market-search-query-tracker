"""Unit tests for eBay Browse API fetch logic with mocked HTTP responses."""
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.ebay_finding import RawListing, _fetch_page, fetch_all_listings

_FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def _load_fixture(name: str) -> str:
    return (_FIXTURES / name).read_text(encoding="utf-8")


def _make_response(text: str, status_code: int = 200) -> httpx.Response:
    """Build a fake httpx.Response with the given body and status."""
    resp = httpx.Response(
        status_code=status_code,
        text=text,
        request=httpx.Request("GET", "https://api.ebay.com/buy/browse/v1/item_summary/search"),
    )
    return resp


def _make_settings(**overrides):
    """Return a minimal mock Settings object for Browse API calls."""
    defaults = dict(
        ebay_app_id="fake-app-id",
        ebay_cert_id="fake-cert-id",
        ebay_site_id="EBAY-GB",
        ebay_max_pages=10,
        ebay_results_per_page=100,
        ebay_request_timeout_seconds=5.0,
        ebay_retry_attempts=3,
        ebay_retry_backoff_seconds=0.0,  # no real waiting in tests
    )
    defaults.update(overrides)
    s = MagicMock()
    for k, v in defaults.items():
        setattr(s, k, v)
    return s


# Patch OAuth token for all tests
@pytest.fixture(autouse=True)
def mock_oauth_token():
    with patch("app.services.ebay_finding._get_access_token", new_callable=AsyncMock, return_value="fake-oauth-token"):
        yield


# ── Single page ────────────────────────────────────────────────────────────


class TestFetchAllListingsSinglePage:
    async def test_returns_three_listings(self):
        body = _load_fixture("browse_single_page.json")
        mock_client = AsyncMock()
        mock_client.get.return_value = _make_response(body)

        with patch("app.services.ebay_finding.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            listings = await fetch_all_listings("nintendo switch", settings=_make_settings())

        assert len(listings) == 3

    async def test_first_listing_fields(self):
        body = _load_fixture("browse_single_page.json")
        mock_client = AsyncMock()
        mock_client.get.return_value = _make_response(body)

        with patch("app.services.ebay_finding.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            listings = await fetch_all_listings("nintendo switch", settings=_make_settings())

        first = listings[0]
        assert first.item_id == "111111111"
        assert first.title == "Nintendo Switch OLED White"
        assert first.current_price == Decimal("259.99")
        assert first.currency == "GBP"
        assert first.buy_it_now is True
        assert first.listing_type == "FixedPrice"

    async def test_http_get_called_once(self):
        body = _load_fixture("browse_single_page.json")
        mock_client = AsyncMock()
        mock_client.get.return_value = _make_response(body)

        with patch("app.services.ebay_finding.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            await fetch_all_listings("nintendo switch", settings=_make_settings())

        assert mock_client.get.call_count == 1


# ── Multi-page pagination ─────────────────────────────────────────────────


class TestFetchAllListingsMultiPage:
    async def test_fetches_both_pages(self):
        page1 = _load_fixture("browse_page1.json")
        page2 = _load_fixture("browse_page2.json")
        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            _make_response(page1),
            _make_response(page2),
        ]

        with patch("app.services.ebay_finding.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            listings = await fetch_all_listings(
                "nintendo switch",
                settings=_make_settings(ebay_results_per_page=3),
            )

        assert len(listings) == 5
        assert mock_client.get.call_count == 2

    async def test_contains_page2_items(self):
        page1 = _load_fixture("browse_page1.json")
        page2 = _load_fixture("browse_page2.json")
        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            _make_response(page1),
            _make_response(page2),
        ]

        with patch("app.services.ebay_finding.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            listings = await fetch_all_listings(
                "nintendo switch",
                settings=_make_settings(ebay_results_per_page=3),
            )

        ids = {l.item_id for l in listings}
        assert "444444444" in ids
        assert "555555555" in ids

    async def test_max_pages_limits_fetches(self):
        page1 = _load_fixture("browse_page1.json")  # total=5
        mock_client = AsyncMock()
        mock_client.get.return_value = _make_response(page1)

        with patch("app.services.ebay_finding.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            listings = await fetch_all_listings(
                "nintendo switch",
                settings=_make_settings(ebay_max_pages=1, ebay_results_per_page=3),
            )

        assert mock_client.get.call_count == 1
        assert len(listings) == 3

    async def test_stop_request_halts_before_next_page(self):
        page1 = _load_fixture("browse_page1.json")
        page2 = _load_fixture("browse_page2.json")
        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            _make_response(page1),
            _make_response(page2),
        ]

        should_cancel_calls = 0

        def should_cancel() -> bool:
            nonlocal should_cancel_calls
            should_cancel_calls += 1
            return should_cancel_calls >= 2

        with patch("app.services.ebay_finding.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            listings = await fetch_all_listings(
                "nintendo switch",
                settings=_make_settings(ebay_results_per_page=3),
                should_cancel=should_cancel,
            )

        assert mock_client.get.call_count == 1
        assert len(listings) == 3


# ── Empty results ──────────────────────────────────────────────────────────


class TestFetchAllListingsEmpty:
    async def test_empty_results_returns_empty_list(self):
        body = _load_fixture("browse_empty.json")
        mock_client = AsyncMock()
        mock_client.get.return_value = _make_response(body)

        with patch("app.services.ebay_finding.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            listings = await fetch_all_listings("xyznoexist", settings=_make_settings())

        assert listings == []


# ── Retry on HTTP 429 ─────────────────────────────────────────────────────


class TestRetryOn429:
    async def test_retries_and_succeeds(self):
        body = _load_fixture("browse_single_page.json")

        err_response = _make_response("rate limited", status_code=429)
        ok_response = _make_response(body)

        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            httpx.HTTPStatusError("429", request=err_response.request, response=err_response),
            ok_response,
        ]

        with patch("app.services.ebay_finding.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            with patch("app.services.ebay_finding.asyncio.sleep", new_callable=AsyncMock):
                listings = await fetch_all_listings("nintendo switch", settings=_make_settings())

        assert len(listings) == 3
        assert mock_client.get.call_count == 2


# ── Retry on HTTP 500 ─────────────────────────────────────────────────────


class TestRetryOn500:
    async def test_retries_server_error(self):
        body = _load_fixture("browse_single_page.json")

        err_response = _make_response("server error", status_code=500)
        ok_response = _make_response(body)

        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            httpx.HTTPStatusError("500", request=err_response.request, response=err_response),
            ok_response,
        ]

        with patch("app.services.ebay_finding.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            with patch("app.services.ebay_finding.asyncio.sleep", new_callable=AsyncMock):
                listings = await fetch_all_listings("nintendo switch", settings=_make_settings())

        assert len(listings) == 3


# ── Non-retryable HTTP error ──────────────────────────────────────────────


class TestNonRetryableError:
    async def test_403_raises_immediately(self):
        err_response = _make_response("forbidden", status_code=403)
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.HTTPStatusError(
            "403", request=err_response.request, response=err_response,
        )

        with patch("app.services.ebay_finding.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            with pytest.raises(httpx.HTTPStatusError):
                await fetch_all_listings("test", settings=_make_settings())

        # Should NOT have retried — only 1 call
        assert mock_client.get.call_count == 1


# ── Timeout retry ─────────────────────────────────────────────────────────


class TestTimeoutRetry:
    async def test_timeout_retries_then_succeeds(self):
        body = _load_fixture("browse_single_page.json")
        ok_response = _make_response(body)

        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            httpx.TimeoutException("timed out"),
            ok_response,
        ]

        with patch("app.services.ebay_finding.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            with patch("app.services.ebay_finding.asyncio.sleep", new_callable=AsyncMock):
                listings = await fetch_all_listings("nintendo switch", settings=_make_settings())

        assert len(listings) == 3
        assert mock_client.get.call_count == 2

    async def test_all_timeouts_exhausted_raises(self):
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.TimeoutException("timed out")

        with patch("app.services.ebay_finding.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            with patch("app.services.ebay_finding.asyncio.sleep", new_callable=AsyncMock):
                with pytest.raises(httpx.TimeoutException):
                    await fetch_all_listings("test", settings=_make_settings())

        assert mock_client.get.call_count == 3  # ebay_retry_attempts=3
