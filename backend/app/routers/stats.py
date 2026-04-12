from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy import func, select, text, union, union_all
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.listing import ListingRecord
from app.models.snapshot import Snapshot
from app.models.sold import SoldRecord
from app.routers.auth import verify_token
from app.schemas.stats import ItemsEvaluated, PriceTrendPoint, QuerySummary, SoldTrendPoint, VelocityPoint

router = APIRouter(prefix="/stats", tags=["stats"])


def _trunc_interval(interval: str) -> str:
    mapping = {"day": "day", "week": "week", "month": "month"}
    return mapping.get(interval, "day")


@router.get("/price-trend", response_model=list[PriceTrendPoint], dependencies=[Depends(verify_token)])
async def price_trend(
    query_id: int,
    granularity: str = "week",
    db: AsyncSession = Depends(get_db),
):
    logger.info("[ROUTER] GET /stats/price-trend query_id={qid} granularity={gr}", qid=query_id, gr=granularity)
    trunc = _trunc_interval(granularity)
    stmt = text("""
        SELECT date_trunc(:trunc, last_seen_at) AS date,
               AVG(current_price)              AS avg_price,
               MIN(current_price)              AS min_price,
               MAX(current_price)              AS max_price,
               COUNT(*)                        AS count
        FROM listing_records
        WHERE query_id = :qid AND current_price IS NOT NULL
        GROUP BY 1 ORDER BY 1
    """)
    result = await db.execute(stmt, {"trunc": trunc, "qid": query_id})
    rows = result.fetchall()
    return [
        PriceTrendPoint(
            date=r.date,
            avg_price=float(r.avg_price) if r.avg_price is not None else None,
            min_price=float(r.min_price) if r.min_price is not None else None,
            max_price=float(r.max_price) if r.max_price is not None else None,
            count=r.count,
        )
        for r in rows
    ]


@router.get("/sold-trend", response_model=list[SoldTrendPoint], dependencies=[Depends(verify_token)])
async def sold_trend(
    query_id: int,
    granularity: str = "week",
    db: AsyncSession = Depends(get_db),
):
    trunc = _trunc_interval(granularity)
    stmt = text("""
        SELECT date_trunc(:trunc, sold_date) AS date,
               AVG(sold_price)               AS avg_price,
               MIN(sold_price)               AS min_price,
               MAX(sold_price)               AS max_price,
               COUNT(*)                      AS count
        FROM sold_records
        WHERE query_id = :qid AND sold_price IS NOT NULL
        GROUP BY 1 ORDER BY 1
    """)
    result = await db.execute(stmt, {"trunc": trunc, "qid": query_id})
    rows = result.fetchall()
    return [
        SoldTrendPoint(
            date=r.date,
            avg_price=float(r.avg_price) if r.avg_price is not None else None,
            min_price=float(r.min_price) if r.min_price is not None else None,
            max_price=float(r.max_price) if r.max_price is not None else None,
            count=r.count,
        )
        for r in rows
    ]


@router.get("/velocity", response_model=list[VelocityPoint], dependencies=[Depends(verify_token)])
async def velocity(
    query_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Snapshot)
        .where(Snapshot.query_id == query_id, Snapshot.status == "complete")
        .order_by(Snapshot.started_at.asc())
    )
    snaps = result.scalars().all()
    return [
        VelocityPoint(
            snapshot_id=s.id,
            started_at=s.started_at,
            items_found=s.items_found,
            items_new=s.items_new,
            items_updated=s.items_updated,
        )
        for s in snaps
    ]


@router.get("/summary", response_model=QuerySummary, dependencies=[Depends(verify_token)])
async def summary(query_id: int, db: AsyncSession = Depends(get_db)):
    logger.info("[ROUTER] GET /stats/summary query_id={qid}", qid=query_id)

    live_count_r = await db.execute(select(func.count()).where(ListingRecord.query_id == query_id))
    total_live = live_count_r.scalar_one()

    sold_count_r = await db.execute(select(func.count()).where(SoldRecord.query_id == query_id))
    total_sold = sold_count_r.scalar_one()

    avg_live_r = await db.execute(select(func.avg(ListingRecord.current_price)).where(ListingRecord.query_id == query_id))
    avg_live = avg_live_r.scalar_one()

    avg_sold_r = await db.execute(select(func.avg(SoldRecord.sold_price)).where(SoldRecord.query_id == query_id))
    avg_sold = avg_sold_r.scalar_one()

    # Median via percentile_cont (PostgreSQL specific)
    median_result = await db.execute(
        text("SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY sold_price) FROM sold_records WHERE query_id = :qid"),
        {"qid": query_id},
    )
    median_sold = median_result.scalar_one()

    price_delta = None
    if avg_sold is not None and avg_live is not None:
        price_delta = float(avg_sold) - float(avg_live)

    return QuerySummary(
        query_id=query_id,
        total_live=total_live,
        total_sold=total_sold,
        avg_live_price=float(avg_live) if avg_live is not None else None,
        avg_sold_price=float(avg_sold) if avg_sold is not None else None,
        median_sold_price=float(median_sold) if median_sold is not None else None,
        price_delta=price_delta,
    )


@router.get("/items-evaluated", response_model=ItemsEvaluated, dependencies=[Depends(verify_token)])
async def items_evaluated(db: AsyncSession = Depends(get_db)):
    from app.services.poll_runner import _running_jobs

    unique_item_ids = union(
        select(ListingRecord.item_id.label("item_id")).where(ListingRecord.item_id.is_not(None)),
        select(SoldRecord.item_id.label("item_id")).where(SoldRecord.item_id.is_not(None)),
    ).subquery()
    total_r = await db.execute(select(func.count()).select_from(unique_item_ids))
    total = total_r.scalar_one() or 0

    observed_at = union_all(
        select(ListingRecord.first_seen_at.label("observed_at")).where(ListingRecord.item_id.is_not(None)),
        select(SoldRecord.scraped_at.label("observed_at")).where(SoldRecord.item_id.is_not(None)),
    ).subquery()
    since_r = await db.execute(select(func.min(observed_at.c.observed_at)))
    since = since_r.scalar_one()

    scheduler_running = len(_running_jobs) > 0
    return ItemsEvaluated(total=total, since=since, scheduler_running=scheduler_running)
