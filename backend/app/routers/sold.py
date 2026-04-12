from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.sold import SoldRecord
from app.routers.auth import verify_token
from app.schemas.sold import SoldList, SoldRead

router = APIRouter(prefix="/sold", tags=["sold"])


@router.get("", response_model=SoldList, dependencies=[Depends(verify_token)])
async def list_sold(
    query_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    search: str | None = None,
    sort: str = "sold_date_desc",
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
):
    logger.info("[ROUTER] GET /sold query_id={qid} page={pg}", qid=query_id, pg=page)
    stmt = select(SoldRecord)

    if query_id is not None:
        stmt = stmt.where(SoldRecord.query_id == query_id)
    if min_price is not None:
        stmt = stmt.where(SoldRecord.sold_price >= min_price)
    if max_price is not None:
        stmt = stmt.where(SoldRecord.sold_price <= max_price)
    if date_from is not None:
        stmt = stmt.where(SoldRecord.sold_date >= date_from)
    if date_to is not None:
        stmt = stmt.where(SoldRecord.sold_date <= date_to)
    if search:
        stmt = stmt.where(SoldRecord.title.ilike(f"%{search}%"))

    total_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = total_result.scalar_one()

    sort_map = {
        "sold_date_desc": SoldRecord.sold_date.desc(),
        "sold_date_asc": SoldRecord.sold_date.asc(),
        "price_asc": SoldRecord.sold_price.asc(),
        "price_desc": SoldRecord.sold_price.desc(),
    }
    order_col = sort_map.get(sort, SoldRecord.sold_date.desc())
    stmt = stmt.order_by(order_col).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    items = result.scalars().all()
    logger.info("[ROUTER] GET /sold → {n} items (total={total})", n=len(items), total=total)
    return SoldList(items=[SoldRead.model_validate(s) for s in items], total=total, page=page, page_size=page_size)


@router.get("/{sold_id}", response_model=SoldRead, dependencies=[Depends(verify_token)])
async def get_sold(sold_id: int, db: AsyncSession = Depends(get_db)):
    s = await db.get(SoldRecord, sold_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Sold record not found")
    return SoldRead.model_validate(s)
