from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class PriceTrendPoint(BaseModel):
    date: datetime
    avg_price: float | None
    min_price: float | None
    max_price: float | None
    count: int


class SoldTrendPoint(BaseModel):
    date: datetime
    avg_price: float | None
    min_price: float | None
    max_price: float | None
    count: int


class VelocityPoint(BaseModel):
    snapshot_id: int
    started_at: datetime
    items_found: int
    items_new: int
    items_updated: int


class QuerySummary(BaseModel):
    query_id: int
    total_live: int
    total_sold: int
    avg_live_price: float | None
    avg_sold_price: float | None
    median_sold_price: float | None
    price_delta: float | None  # avg_sold - avg_live


class ItemsEvaluated(BaseModel):
    total: int
    since: datetime | None
    scheduler_running: bool
