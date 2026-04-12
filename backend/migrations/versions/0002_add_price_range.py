"""Add price range filter — min_price and max_price to search_queries.

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-12 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "search_queries",
        sa.Column("min_price", sa.Numeric(12, 2), nullable=True),
    )
    op.add_column(
        "search_queries",
        sa.Column("max_price", sa.Numeric(12, 2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("search_queries", "max_price")
    op.drop_column("search_queries", "min_price")
