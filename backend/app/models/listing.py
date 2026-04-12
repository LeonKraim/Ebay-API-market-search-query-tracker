from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ListingRecord(Base):
    __tablename__ = "listing_records"
    __table_args__ = (UniqueConstraint("item_id", "snapshot_id", name="uq_item_snapshot"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("snapshots.id", ondelete="CASCADE"), nullable=False
    )
    query_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("search_queries.id", ondelete="CASCADE"), nullable=False
    )
    item_id: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    gallery_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(5), default="GBP", nullable=False)
    buy_it_now: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    listing_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    watch_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bid_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    selling_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    country: Mapped[str | None] = mapped_column(String(10), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    item_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    snapshot: Mapped["Snapshot"] = relationship("Snapshot", back_populates="listings")  # noqa: F821
    query: Mapped["SearchQuery"] = relationship("SearchQuery", back_populates="listings")  # noqa: F821
