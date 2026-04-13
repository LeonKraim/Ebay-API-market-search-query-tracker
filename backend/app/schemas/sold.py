from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class SoldRead(BaseModel):
    id: int
    query_id: int
    item_id: str | None
    title: str | None
    sold_price: Decimal | None
    currency: str
    sold_date: datetime | None
    listing_type: str | None
    image_url: str | None
    item_url: str | None
    source: str = "scraped"
    scraped_at: datetime

    model_config = {"from_attributes": True}


class SoldList(BaseModel):
    items: list[SoldRead]
    total: int
    page: int
    page_size: int
