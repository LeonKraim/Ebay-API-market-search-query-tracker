from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    keyword: Mapped[str] = mapped_column(String(500), nullable=False)
    category_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    site_id: Mapped[str] = mapped_column(String(20), default="EBAY-GB", nullable=False)
    min_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    max_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    interval_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    include_sold: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_polled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_snapshots: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    snapshots: Mapped[list["Snapshot"]] = relationship(  # noqa: F821
        "Snapshot", back_populates="query", cascade="all, delete-orphan"
    )
    listings: Mapped[list["ListingRecord"]] = relationship(  # noqa: F821
        "ListingRecord", back_populates="query", cascade="all, delete-orphan"
    )
    sold_records: Mapped[list["SoldRecord"]] = relationship(  # noqa: F821
        "SoldRecord", back_populates="query", cascade="all, delete-orphan"
    )
