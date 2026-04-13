"""
Poll runner — orchestrates a full snapshot poll cycle for a single search query.

Lifecycle:
  1. Create Snapshot row (status=running)
  2. Fetch live listings from eBay Finding API
  3. [optional] Scrape sold/completed listings
  4. Deduplicate against existing records
  5. Bulk upsert to DB
  6. Close snapshot (status=complete / error)
  7. Update SearchQuery.last_polled_at + total_snapshots
"""
from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from decimal import Decimal

from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.listing import ListingRecord
from app.models.query import SearchQuery
from app.models.snapshot import Snapshot
from app.models.sold import SoldRecord
from app.services.dedup import classify
from app.services.ebay_finding import RawListing, fetch_all_listings
from app.services.sold_scraper import scrape_sold_listings

# Track running jobs to prevent overlap
_running_jobs: set[int] = set()
_running_lock = asyncio.Lock()
_cancel_events: dict[int, asyncio.Event] = {}


async def is_running(query_id: int) -> bool:
    async with _running_lock:
        return query_id in _running_jobs


async def cancel_poll(query_id: int) -> bool:
    """Signal an in-progress poll to stop. Returns True if a running poll was found."""
    async with _running_lock:
        event = _cancel_events.get(query_id)
        if event is not None and query_id in _running_jobs:
            event.set()
            return True
        return False


async def get_running_query_ids() -> list[int]:
    """Return the list of query IDs currently being polled."""
    async with _running_lock:
        return list(_running_jobs)


async def run_poll(query_id: int) -> None:
    """
    Execute a full poll cycle for query_id.
    If a poll for this query is already in progress, skip and log.
    """
    async with _running_lock:
        if query_id in _running_jobs:
            logger.warning(
                "[SCHEDULER] Job for query {qid} still running — skipping this interval",
                qid=query_id,
            )
            return
        _running_jobs.add(query_id)

    cancel_event = asyncio.Event()
    async with _running_lock:
        _cancel_events[query_id] = cancel_event

    start_ts = time.monotonic()
    snapshot_id: int | None = None

    try:
        async with get_session() as session:
            # ── Load query ─────────────────────────────────────────────────
            query = await session.get(SearchQuery, query_id)
            if query is None:
                logger.error("[POLL] Query {qid} not found — aborting", qid=query_id)
                return
            if not query.enabled:
                logger.info("[POLL] Query {qid} '{name}' is disabled — skipping", qid=query_id, name=query.name)
                return

            logger.info(
                "[POLL] Starting snapshot for query #{qid} '{name}' (keyword='{kw}')",
                qid=query_id, name=query.name, kw=query.keyword,
            )

            # ── Create snapshot ────────────────────────────────────────────
            snapshot = Snapshot(query_id=query_id, started_at=datetime.now(timezone.utc), status="running")
            session.add(snapshot)
            await session.flush()
            snapshot_id = snapshot.id
            logger.info("[POLL] Snapshot #{sid} created", sid=snapshot_id)

    # Re-open a fresh session for the eBay calls (they can be slow; don't hold a DB connection)
    except Exception as exc:
        logger.exception("[POLL] Failed to create snapshot for query {qid}: {err}", qid=query_id, err=str(exc))
        async with _running_lock:
            _running_jobs.discard(query_id)
        return

    # ── Fetch from eBay (outside DB session) ──────────────────────────────
    raw_listings: list[RawListing] = []
    sold_items = []
    fetch_error: str | None = None

    try:
        async with get_session() as session:
            query = await session.get(SearchQuery, query_id)

        raw_listings = await fetch_all_listings(
            keyword=query.keyword,
            category_id=query.category_id,
            site_id=query.site_id,
            price_min=query.min_price,
            price_max=query.max_price,
            should_cancel=cancel_event.is_set,
        )

        if query.include_sold:
            sold_items = await scrape_sold_listings(keyword=query.keyword, site_id=query.site_id)

    except Exception as exc:
        fetch_error = str(exc)
        logger.error("[POLL] eBay fetch error for snapshot #{sid}: {err}", sid=snapshot_id, err=fetch_error)

    # ── Check for cancellation ─────────────────────────────────────────────
    if cancel_event.is_set():
        logger.info("[POLL] Query {qid} poll was cancelled — discarding fetched data", qid=query_id)
        async with _running_lock:
            _running_jobs.discard(query_id)
            _cancel_events.pop(query_id, None)
        try:
            async with get_session() as session:
                snapshot = await session.get(Snapshot, snapshot_id)
                if snapshot:
                    snapshot.status = "cancelled"
                    snapshot.error_message = "Cancelled by user"
                    snapshot.finished_at = datetime.now(timezone.utc)
        except Exception:
            pass
        return

    # ── Write to DB ────────────────────────────────────────────────────────
    try:
        async with get_session() as session:
            query = await session.get(SearchQuery, query_id)
            snapshot = await session.get(Snapshot, snapshot_id)

            # Query or snapshot may have been deleted while the poll was in flight
            if query is None or snapshot is None:
                logger.warning(
                    "[POLL] Query {qid} or snapshot {sid} was deleted during poll — aborting gracefully",
                    qid=query_id, sid=snapshot_id,
                )
                return

            if fetch_error:
                snapshot.status = "error"
                snapshot.error_message = fetch_error
                snapshot.finished_at = datetime.now(timezone.utc)
                await session.flush()
                logger.error("[POLL] Snapshot #{sid} closed with error", sid=snapshot_id)
                return

            # Load existing item IDs and prices for this query
            result = await session.execute(
                select(ListingRecord.item_id, ListingRecord.current_price)
                .where(ListingRecord.query_id == query_id)
            )
            existing: dict[str, Decimal | None] = {
                row.item_id: row.current_price for row in result
            }

            # Dedup
            dedup = classify(raw_listings, existing)

            # Build rows for new listings
            new_rows = [
                {
                    "snapshot_id": snapshot_id,
                    "query_id": query_id,
                    "item_id": item.item_id,
                    "title": (item.title or "")[:500],
                    "gallery_url": item.gallery_url,
                    "image_url": item.image_url,
                    "current_price": item.current_price,
                    "currency": item.currency,
                    "buy_it_now": item.buy_it_now,
                    "listing_type": item.listing_type,
                    "watch_count": item.watch_count,
                    "bid_count": item.bid_count,
                    "selling_state": item.selling_state,
                    "country": item.country,
                    "postal_code": item.postal_code,
                    "end_time": item.end_time,
                    "item_url": item.item_url,
                    "first_seen_at": datetime.now(timezone.utc),
                    "last_seen_at": datetime.now(timezone.utc),
                }
                for item in dedup.new
            ]

            # Insert new listings with ON CONFLICT DO NOTHING
            # Chunk into batches of 3,000 rows to stay under PostgreSQL's 65,535 bind-parameter limit
            # (19 columns × 3,000 rows = 57,000 params — safely under the hard limit)
            _LISTING_BATCH_SIZE = 3_000
            if new_rows:
                for _batch_start in range(0, len(new_rows), _LISTING_BATCH_SIZE):
                    _batch = new_rows[_batch_start : _batch_start + _LISTING_BATCH_SIZE]
                    stmt = pg_insert(ListingRecord).values(_batch)
                    stmt = stmt.on_conflict_do_nothing(index_elements=["item_id", "snapshot_id"])
                    await session.execute(stmt)
                logger.info(
                    "[DB] listing_records: {n} new rows inserted (snapshot #{sid})",
                    n=len(new_rows), sid=snapshot_id,
                )

            # Update changed listings
            for item in dedup.updated:
                await session.execute(
                    update(ListingRecord)
                    .where(ListingRecord.item_id == item.item_id, ListingRecord.query_id == query_id)
                    .values(
                        current_price=item.current_price,
                        last_seen_at=datetime.now(timezone.utc),
                        snapshot_id=snapshot_id,
                    )
                )
            if dedup.updated:
                logger.info("[DB] listing_records: {n} rows updated", n=len(dedup.updated))

            # Insert sold records
            if sold_items:
                sold_rows = [
                    {
                        "query_id": query_id,
                        "item_id": s.item_id,
                        "title": (s.title or "")[:500],
                        "sold_price": s.sold_price,
                        "currency": s.currency,
                        "sold_date": s.sold_date,
                        "listing_type": s.listing_type,
                        "image_url": s.image_url,
                        "item_url": s.item_url,
                        "scraped_at": datetime.now(timezone.utc),
                    }
                    for s in sold_items
                ]
                sold_stmt = pg_insert(SoldRecord).values(sold_rows)
                sold_stmt = sold_stmt.on_conflict_do_nothing(index_elements=["item_id", "sold_date"])
                await session.execute(sold_stmt)
                logger.info("[DB] sold_records: {n} rows inserted (ON CONFLICT DO NOTHING)", n=len(sold_rows))

            # Close snapshot
            elapsed = time.monotonic() - start_ts
            snapshot.status = "complete"
            snapshot.finished_at = datetime.now(timezone.utc)
            snapshot.items_found = len(raw_listings)
            snapshot.items_new = len(dedup.new)
            snapshot.items_updated = len(dedup.updated)

            # Update query stats
            query.last_polled_at = datetime.now(timezone.utc)
            query.total_snapshots = (query.total_snapshots or 0) + 1

            await session.flush()

            logger.info(
                "[POLL] Snapshot #{sid} complete — {found} found, {new} new, "
                "{upd} updated, {sold} sold, {elapsed:.1f}s",
                sid=snapshot_id,
                found=len(raw_listings),
                new=len(dedup.new),
                upd=len(dedup.updated),
                sold=len(sold_items),
                elapsed=elapsed,
            )

    except Exception as exc:
        logger.exception(
            "[POLL] DB write error for snapshot #{sid}: {err}", sid=snapshot_id, err=str(exc)
        )
        # Attempt to mark snapshot as error
        try:
            async with get_session() as session:
                snapshot = await session.get(Snapshot, snapshot_id)
                if snapshot:
                    snapshot.status = "error"
                    snapshot.error_message = str(exc)
                    snapshot.finished_at = datetime.now(timezone.utc)
        except Exception:
            pass

    finally:
        async with _running_lock:
            _running_jobs.discard(query_id)
            _cancel_events.pop(query_id, None)
