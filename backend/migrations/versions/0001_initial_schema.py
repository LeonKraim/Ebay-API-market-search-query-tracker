"""Initial schema — all four tables.

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── search_queries ─────────────────────────────────────────────────
    op.create_table(
        "search_queries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("category_id", sa.String(length=64), nullable=True),
        sa.Column("site_id", sa.String(length=32), nullable=False, server_default="EBAY-GB"),
        sa.Column("interval_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("include_sold", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_polled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_snapshots", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_search_queries_keyword", "search_queries", ["keyword"])
    op.create_index("ix_search_queries_enabled", "search_queries", ["enabled"])

    # ── snapshots ──────────────────────────────────────────────────────
    op.create_table(
        "snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("query_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("items_found", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_new", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="running"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["query_id"], ["search_queries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_snapshots_query_id", "snapshots", ["query_id"])
    op.create_index("ix_snapshots_started_at", "snapshots", ["started_at"])
    op.create_index("ix_snapshots_status", "snapshots", ["status"])

    # ── listing_records ────────────────────────────────────────────────
    op.create_table(
        "listing_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("snapshot_id", sa.Integer(), nullable=False),
        sa.Column("query_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=2048), nullable=True),
        sa.Column("gallery_url", sa.String(length=2048), nullable=True),
        sa.Column("current_price", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=True),
        sa.Column("buy_it_now", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("listing_type", sa.String(length=64), nullable=True),
        sa.Column("watch_count", sa.Integer(), nullable=True),
        sa.Column("bid_count", sa.Integer(), nullable=True),
        sa.Column("selling_state", sa.String(length=64), nullable=True),
        sa.Column("country", sa.String(length=8), nullable=True),
        sa.Column("postal_code", sa.String(length=16), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("item_url", sa.String(length=2048), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["snapshot_id"], ["snapshots.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["query_id"], ["search_queries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("item_id", "snapshot_id", name="uq_listing_item_snapshot"),
    )
    op.create_index("ix_listing_records_item_id", "listing_records", ["item_id"])
    op.create_index("ix_listing_records_query_id", "listing_records", ["query_id"])
    op.create_index("ix_listing_records_current_price", "listing_records", ["current_price"])

    # ── sold_records ───────────────────────────────────────────────────
    op.create_table(
        "sold_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("query_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("sold_price", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=True),
        sa.Column("sold_date", sa.Date(), nullable=True),
        sa.Column("listing_type", sa.String(length=64), nullable=True),
        sa.Column("image_url", sa.String(length=2048), nullable=True),
        sa.Column("item_url", sa.String(length=2048), nullable=True),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["query_id"], ["search_queries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("item_id", "sold_date", name="uq_sold_item_date"),
    )
    op.create_index("ix_sold_records_query_id", "sold_records", ["query_id"])
    op.create_index("ix_sold_records_sold_date", "sold_records", ["sold_date"])
    op.create_index("ix_sold_records_sold_price", "sold_records", ["sold_price"])


def downgrade() -> None:
    op.drop_table("sold_records")
    op.drop_table("listing_records")
    op.drop_table("snapshots")
    op.drop_table("search_queries")
