"""Unit tests for the poll runner orchestration with mocked eBay API + DB."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from app.services.ebay_finding import RawListing
from app.services.sold_scraper import RawSoldItem


def _make_raw_listings(count: int = 2) -> list[RawListing]:
    return [
        RawListing(
            item_id=str(100 + i),
            title=f"Test Item {i}",
            current_price=Decimal("10.00") + i,
            currency="GBP",
            buy_it_now=True,
            listing_type="FixedPrice",
            selling_state="Active",
        )
        for i in range(count)
    ]


def _make_sold_items(count: int = 1) -> list[RawSoldItem]:
    from datetime import date

    return [
        RawSoldItem(
            item_id=str(900 + i),
            title=f"Sold Item {i}",
            sold_price=50.0 + i,
            currency="GBP",
            sold_date=date(2026, 3, 10),
            listing_type="Auction",
            image_url=None,
            item_url=f"https://www.ebay.co.uk/itm/{900 + i}",
        )
        for i in range(count)
    ]


def _make_query(
    query_id: int = 1,
    enabled: bool = True,
    include_sold: bool = True,
) -> MagicMock:
    q = MagicMock()
    q.id = query_id
    q.name = "Test Query"
    q.keyword = "nintendo switch"
    q.category_id = None
    q.site_id = "EBAY-GB"
    q.min_price = None
    q.max_price = None
    q.interval_minutes = 60
    q.enabled = enabled
    q.include_sold = include_sold
    q.total_snapshots = 0
    q.last_polled_at = None
    return q


def _make_snapshot(snapshot_id: int = 10) -> MagicMock:
    snap = MagicMock()
    snap.id = snapshot_id
    snap.status = "running"
    snap.error_message = None
    snap.finished_at = None
    snap.items_found = 0
    snap.items_new = 0
    snap.items_updated = 0
    return snap


class _FakeSessionCM:
    """Fake async context manager that yields the same mock session."""

    def __init__(self, session):
        self._session = session

    async def __aenter__(self):
        return self._session

    async def __aexit__(self, *args):
        pass


# ── Happy path ─────────────────────────────────────────────────────────────


class TestRunPollHappyPath:
    async def test_creates_snapshot_and_inserts(self):
        from app.services.poll_runner import _running_jobs, run_poll

        # Ensure clean state
        _running_jobs.discard(1)

        query = _make_query()
        snap = _make_snapshot()
        raw = _make_raw_listings(2)
        sold = _make_sold_items(1)

        session = AsyncMock()
        # session.get returns query on first call, query again, then query+snapshot together
        session.get.side_effect = [query, query, query, snap]
        session.flush = AsyncMock()
        # session.execute returns empty existing listings
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([]))
        session.execute = AsyncMock(return_value=mock_result)

        # session.add is sync in SQLAlchemy — use MagicMock to avoid unawaited coroutine warning
        def _add_side_effect(obj):
            if hasattr(obj, "status") and obj.status == "running":
                obj.id = 10

        session.add = MagicMock(side_effect=_add_side_effect)

        with (
            patch("app.services.poll_runner.get_session", return_value=_FakeSessionCM(session)),
            patch("app.services.poll_runner.fetch_all_listings", new_callable=AsyncMock, return_value=raw),
            patch("app.services.poll_runner.scrape_sold_listings", new_callable=AsyncMock, return_value=sold),
            patch("app.services.poll_runner.classify") as mock_classify,
        ):
            dedup_result = MagicMock()
            dedup_result.new = raw
            dedup_result.updated = []
            mock_classify.return_value = dedup_result

            await run_poll(1)

        # Verify session was used
        assert session.add.called
        assert session.execute.called

    async def test_fetch_all_listings_called_with_keyword(self):
        from app.services.poll_runner import _running_jobs, run_poll

        _running_jobs.discard(1)

        query = _make_query()
        snap = _make_snapshot()

        session = AsyncMock()
        session.get.side_effect = [query, query, query, snap]
        session.flush = AsyncMock()
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([]))
        session.execute = AsyncMock(return_value=mock_result)

        def _add_side_effect(obj):
            if hasattr(obj, "status") and getattr(obj, "status", None) == "running":
                obj.id = 10

        session.add = MagicMock(side_effect=_add_side_effect)

        mock_fetch = AsyncMock(return_value=_make_raw_listings(1))

        with (
            patch("app.services.poll_runner.get_session", return_value=_FakeSessionCM(session)),
            patch("app.services.poll_runner.fetch_all_listings", mock_fetch),
            patch("app.services.poll_runner.scrape_sold_listings", new_callable=AsyncMock, return_value=[]),
            patch("app.services.poll_runner.classify") as mock_classify,
        ):
            dedup_result = MagicMock()
            dedup_result.new = _make_raw_listings(1)
            dedup_result.updated = []
            mock_classify.return_value = dedup_result

            await run_poll(1)

        mock_fetch.assert_called_once_with(
            keyword="nintendo switch",
            category_id=None,
            site_id="EBAY-GB",
            price_min=None,
            price_max=None,
            should_cancel=ANY,
        )


# ── Concurrent job guard ──────────────────────────────────────────────────


class TestConcurrentJobGuard:
    async def test_skips_when_already_running(self):
        from app.services.poll_runner import _running_jobs, _running_lock, run_poll

        async with _running_lock:
            _running_jobs.add(99)

        with patch("app.services.poll_runner.get_session") as mock_gs:
            await run_poll(99)

        # get_session should NOT have been called — we skipped
        mock_gs.assert_not_called()

        # Cleanup
        async with _running_lock:
            _running_jobs.discard(99)


# ── Query not found ───────────────────────────────────────────────────────


class TestQueryNotFound:
    async def test_aborts_when_query_missing(self):
        from app.services.poll_runner import _running_jobs, run_poll

        _running_jobs.discard(999)

        session = AsyncMock()
        session.get.return_value = None  # query not found
        session.flush = AsyncMock()

        with patch("app.services.poll_runner.get_session", return_value=_FakeSessionCM(session)):
            await run_poll(999)

        # Should NOT have tried to create a snapshot (no add call with a Snapshot)
        # The function returns early — no crash
        assert True  # If we reach here, no exception was raised


# ── Query disabled ────────────────────────────────────────────────────────


class TestQueryDisabled:
    async def test_skips_disabled_query(self):
        from app.services.poll_runner import _running_jobs, run_poll

        _running_jobs.discard(2)

        query = _make_query(query_id=2, enabled=False)
        session = AsyncMock()
        session.get.return_value = query
        session.flush = AsyncMock()

        mock_fetch = AsyncMock()

        with (
            patch("app.services.poll_runner.get_session", return_value=_FakeSessionCM(session)),
            patch("app.services.poll_runner.fetch_all_listings", mock_fetch),
        ):
            await run_poll(2)

        # fetch_all_listings should NOT have been called
        mock_fetch.assert_not_called()


# ── eBay fetch error ──────────────────────────────────────────────────────


class TestFetchError:
    async def test_snapshot_marked_error_on_fetch_failure(self):
        from app.services.poll_runner import _running_jobs, run_poll

        _running_jobs.discard(3)

        query = _make_query(query_id=3)
        snap = _make_snapshot(snapshot_id=20)

        session = AsyncMock()
        session.get.side_effect = [query, query, query, snap]
        session.flush = AsyncMock()

        def _add_side_effect(obj):
            if hasattr(obj, "status") and getattr(obj, "status", None) == "running":
                obj.id = 20

        session.add = MagicMock(side_effect=_add_side_effect)

        with (
            patch("app.services.poll_runner.get_session", return_value=_FakeSessionCM(session)),
            patch(
                "app.services.poll_runner.fetch_all_listings",
                new_callable=AsyncMock,
                side_effect=Exception("API timeout"),
            ),
        ):
            await run_poll(3)

        # After the error path, snapshot should be marked as error
        assert snap.status == "error"
        assert "API timeout" in snap.error_message


# ── include_sold=False ────────────────────────────────────────────────────


class TestIncludeSoldFalse:
    async def test_does_not_scrape_sold_when_disabled(self):
        from app.services.poll_runner import _running_jobs, run_poll

        _running_jobs.discard(4)

        query = _make_query(query_id=4, include_sold=False)
        snap = _make_snapshot(snapshot_id=30)

        session = AsyncMock()
        session.get.side_effect = [query, query, query, snap]
        session.flush = AsyncMock()
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([]))
        session.execute = AsyncMock(return_value=mock_result)

        def _add_side_effect(obj):
            if hasattr(obj, "status") and getattr(obj, "status", None) == "running":
                obj.id = 30

        session.add = MagicMock(side_effect=_add_side_effect)

        mock_scrape = AsyncMock(return_value=[])

        with (
            patch("app.services.poll_runner.get_session", return_value=_FakeSessionCM(session)),
            patch("app.services.poll_runner.fetch_all_listings", new_callable=AsyncMock, return_value=[]),
            patch("app.services.poll_runner.scrape_sold_listings", mock_scrape),
            patch("app.services.poll_runner.classify") as mock_classify,
        ):
            dedup_result = MagicMock()
            dedup_result.new = []
            dedup_result.updated = []
            mock_classify.return_value = dedup_result

            await run_poll(4)

        mock_scrape.assert_not_called()
