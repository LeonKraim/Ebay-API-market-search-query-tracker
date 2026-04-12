from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.snapshot import Snapshot
from app.models.listing import ListingRecord
from app.routers.auth import verify_token
from app.schemas.listing import ListingList, ListingRead
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


class SnapshotRead(BaseModel):
    id: int
    query_id: int
    started_at: datetime
    finished_at: datetime | None
    items_found: int
    items_new: int
    items_updated: int
    status: str
    error_message: str | None
    model_config = {"from_attributes": True}


class SnapshotList(BaseModel):
    items: list[SnapshotRead]
    total: int


@router.get("", response_model=SnapshotList, dependencies=[Depends(verify_token)])
async def list_snapshots(
    query_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
):
    logger.info("[ROUTER] GET /snapshots query_id={qid} status={st}", qid=query_id, st=status)
    stmt = select(Snapshot).order_by(Snapshot.started_at.desc())
    if query_id is not None:
        stmt = stmt.where(Snapshot.query_id == query_id)
    if status is not None:
        stmt = stmt.where(Snapshot.status == status)

    total_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = total_result.scalar_one()
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return SnapshotList(items=[SnapshotRead.model_validate(s) for s in items], total=total)


@router.get("/{snapshot_id}", response_model=SnapshotRead, dependencies=[Depends(verify_token)])
async def get_snapshot(snapshot_id: int, db: AsyncSession = Depends(get_db)):
    s = await db.get(Snapshot, snapshot_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return SnapshotRead.model_validate(s)


@router.get("/{snapshot_id}/listings", response_model=ListingList, dependencies=[Depends(verify_token)])
async def snapshot_listings(
    snapshot_id: int,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
):
    snap = await db.get(Snapshot, snapshot_id)
    if snap is None:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    total_result = await db.execute(
        select(func.count()).where(ListingRecord.snapshot_id == snapshot_id)
    )
    total = total_result.scalar_one()
    result = await db.execute(
        select(ListingRecord)
        .where(ListingRecord.snapshot_id == snapshot_id)
        .offset((page - 1) * page_size).limit(page_size)
    )
    items = result.scalars().all()
    return ListingList(items=[ListingRead.model_validate(l) for l in items], total=total, page=page, page_size=page_size)
