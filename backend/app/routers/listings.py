from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.listing import ListingRecord
from app.routers.auth import verify_token
from app.schemas.listing import ListingList, ListingRead

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("", response_model=ListingList, dependencies=[Depends(verify_token)])
async def list_listings(
    query_id: int | None = None,
    snapshot_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    buy_it_now: bool | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    search: str | None = None,
    sort: str = "last_seen_at_desc",
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
):
    logger.info("[ROUTER] GET /listings query_id={qid} page={pg}", qid=query_id, pg=page)
    stmt = select(ListingRecord)

    if query_id is not None:
        stmt = stmt.where(ListingRecord.query_id == query_id)
    if snapshot_id is not None:
        stmt = stmt.where(ListingRecord.snapshot_id == snapshot_id)
    if min_price is not None:
        stmt = stmt.where(ListingRecord.current_price >= min_price)
    if max_price is not None:
        stmt = stmt.where(ListingRecord.current_price <= max_price)
    if buy_it_now is not None:
        stmt = stmt.where(ListingRecord.buy_it_now == buy_it_now)
    if date_from is not None:
        stmt = stmt.where(ListingRecord.last_seen_at >= date_from)
    if date_to is not None:
        stmt = stmt.where(ListingRecord.last_seen_at <= date_to)
    if search:
        stmt = stmt.where(ListingRecord.title.ilike(f"%{search}%"))

    total_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = total_result.scalar_one()

    # Sorting
    sort_map = {
        "last_seen_at_desc": ListingRecord.last_seen_at.desc(),
        "last_seen_at_asc": ListingRecord.last_seen_at.asc(),
        "price_asc": ListingRecord.current_price.asc(),
        "price_desc": ListingRecord.current_price.desc(),
    }
    order_col = sort_map.get(sort, ListingRecord.last_seen_at.desc())
    stmt = stmt.order_by(order_col).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    items = result.scalars().all()
    logger.info("[ROUTER] GET /listings → {n} items (total={total})", n=len(items), total=total)
    return ListingList(items=[ListingRead.model_validate(l) for l in items], total=total, page=page, page_size=page_size)


@router.get("/item/{item_id}", response_model=ListingList, dependencies=[Depends(verify_token)])
async def listing_history(
    item_id: str,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Return all snapshots of a specific eBay item_id (its full price history)."""
    logger.info("[ROUTER] GET /listings/item/{item_id} — price history", item_id=item_id)
    stmt = select(ListingRecord).where(ListingRecord.item_id == item_id).order_by(ListingRecord.first_seen_at.asc())
    total_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = total_result.scalar_one()
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ListingList(items=[ListingRead.model_validate(l) for l in items], total=total, page=page, page_size=page_size)


@router.get("/{listing_id}", response_model=ListingRead, dependencies=[Depends(verify_token)])
async def get_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
    l = await db.get(ListingRecord, listing_id)
    if l is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return ListingRead.model_validate(l)
