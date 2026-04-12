from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ListingRead(BaseModel):
    id: int
    snapshot_id: int
    query_id: int
    item_id: str
    title: str | None
    description: str | None
    image_url: str | None
    gallery_url: str | None
    current_price: Decimal | None
    currency: str
    buy_it_now: bool | None
    listing_type: str | None
    watch_count: int | None
    bid_count: int | None
    selling_state: str | None
    country: str | None
    postal_code: str | None
    end_time: datetime | None
    item_url: str | None
    first_seen_at: datetime
    last_seen_at: datetime

    model_config = {"from_attributes": True}


class ListingList(BaseModel):
    items: list[ListingRead]
    total: int
    page: int
    page_size: int
