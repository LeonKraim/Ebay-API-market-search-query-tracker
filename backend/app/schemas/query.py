from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class QueryCreate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    keyword: str = Field(..., min_length=1, max_length=500)
    category_id: str | None = Field(default=None, max_length=20)
    site_id: str = Field(default="EBAY-DE", max_length=20)
    min_price: Decimal | None = Field(default=None, ge=0)
    max_price: Decimal | None = Field(default=None, ge=0)
    interval_minutes: int = Field(default=60, ge=5, le=10080)
    enabled: bool = True
    include_sold: bool = True

    @field_validator("keyword", "name")
    @classmethod
    def _no_blank(cls, v: str | None) -> str | None:
        if v is None:
            return None
        stripped = v.strip()
        if not stripped:
            raise ValueError("must not be blank or whitespace-only")
        return stripped


class QueryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    keyword: str | None = Field(default=None, min_length=1, max_length=500)
    category_id: str | None = Field(default=None, max_length=20)
    site_id: str | None = Field(default=None, max_length=20)
    min_price: Decimal | None = Field(default=None, ge=0)
    max_price: Decimal | None = Field(default=None, ge=0)
    interval_minutes: int | None = Field(default=None, ge=5, le=10080)
    enabled: bool | None = None
    include_sold: bool | None = None


class QueryRead(BaseModel):
    id: int
    name: str
    keyword: str
    category_id: str | None
    site_id: str
    min_price: Decimal | None
    max_price: Decimal | None
    interval_minutes: int
    enabled: bool
    include_sold: bool
    created_at: datetime
    last_polled_at: datetime | None
    total_snapshots: int

    model_config = {"from_attributes": True}


class QueryList(BaseModel):
    items: list[QueryRead]
    total: int
