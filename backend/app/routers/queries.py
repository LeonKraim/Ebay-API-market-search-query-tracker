from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.query import SearchQuery
from app.routers.auth import verify_token
from app.scheduler import sync_query_schedule
from app.schemas.query import QueryCreate, QueryList, QueryRead, QueryUpdate
from app.services.poll_runner import run_poll, is_running, cancel_poll, cancel_poll
import asyncio

router = APIRouter(prefix="/queries", tags=["queries"])


def _resolved_query_name(keyword: str, name: str | None) -> str:
    return name or keyword


@router.get("", response_model=QueryList, dependencies=[Depends(verify_token)])
async def list_queries(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    logger.info("[ROUTER] GET /queries page={page}", page=page)
    offset = (page - 1) * page_size
    total_result = await db.execute(select(func.count()).select_from(SearchQuery))
    total = total_result.scalar_one()
    result = await db.execute(select(SearchQuery).offset(offset).limit(page_size).order_by(SearchQuery.created_at.desc()))
    items = result.scalars().all()
    logger.info("[ROUTER] GET /queries → {n} items (total={total})", n=len(items), total=total)
    return QueryList(items=[QueryRead.model_validate(q) for q in items], total=total)


@router.post("", response_model=QueryRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_token)])
async def create_query(body: QueryCreate, db: AsyncSession = Depends(get_db)):
    logger.info("[ROUTER] POST /queries keyword='{kw}'", kw=body.keyword)
    payload = body.model_dump(exclude_unset=True)
    payload["name"] = _resolved_query_name(body.keyword, body.name)
    q = SearchQuery(**payload)
    db.add(q)
    await db.flush()
    await db.refresh(q)
    await sync_query_schedule(q.id, q.enabled, q.interval_minutes)
    logger.info("[ROUTER] Query created id={id} name='{name}'", id=q.id, name=q.name)
    return QueryRead.model_validate(q)


@router.get("/{query_id}", response_model=QueryRead, dependencies=[Depends(verify_token)])
async def get_query(query_id: int, db: AsyncSession = Depends(get_db)):
    logger.debug("[ROUTER] GET /queries/{id}", id=query_id)
    q = await db.get(SearchQuery, query_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Query not found")
    return QueryRead.model_validate(q)


@router.patch("/{query_id}", response_model=QueryRead, dependencies=[Depends(verify_token)])
async def update_query(query_id: int, body: QueryUpdate, db: AsyncSession = Depends(get_db)):
    logger.info("[ROUTER] PATCH /queries/{id}", id=query_id)
    q = await db.get(SearchQuery, query_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Query not found")
    changes = body.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(q, field, value)
    if "keyword" in changes and "name" not in changes:
        q.name = q.keyword
    await db.flush()
    await db.refresh(q)
    await sync_query_schedule(q.id, q.enabled, q.interval_minutes)
    logger.info("[ROUTER] Query #{id} updated", id=query_id)
    return QueryRead.model_validate(q)


@router.delete("/{query_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_token)])
async def delete_query(query_id: int, db: AsyncSession = Depends(get_db)):
    logger.info("[ROUTER] DELETE /queries/{id}", id=query_id)
    if await is_running(query_id):
        raise HTTPException(
            status_code=409,
            detail="This query is currently being polled. Stop the poll using the Stop button first, then delete.",
        )
    q = await db.get(SearchQuery, query_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Query not found")
    await db.delete(q)
    await sync_query_schedule(query_id, False)
    logger.info("[ROUTER] Query #{id} deleted (cascade)", id=query_id)


@router.post("/{query_id}/stop", dependencies=[Depends(verify_token)])
async def stop_query_poll(query_id: int):
    logger.info("[ROUTER] POST /queries/{id}/stop", id=query_id)
    if not await is_running(query_id):
        raise HTTPException(status_code=404, detail="No active poll found for this query")
    await cancel_poll(query_id)
    return {"message": f"Stop requested for query #{query_id}", "query_id": query_id}


@router.post("/{query_id}/stop", dependencies=[Depends(verify_token)])
async def stop_query_poll(query_id: int):
    logger.info("[ROUTER] POST /queries/{id}/stop", id=query_id)
    if not await is_running(query_id):
        raise HTTPException(status_code=404, detail="No active poll found for this query")
    await cancel_poll(query_id)
    return {"message": f"Stop requested for query #{query_id}", "query_id": query_id}


@router.post("/{query_id}/run", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(verify_token)])
async def run_query_now(query_id: int, db: AsyncSession = Depends(get_db)):
    logger.info("[ROUTER] POST /queries/{id}/run — triggering immediate poll", id=query_id)
    q = await db.get(SearchQuery, query_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Query not found")
    asyncio.create_task(run_poll(query_id))
    return {"message": f"Poll triggered for query #{query_id}", "query_id": query_id}
