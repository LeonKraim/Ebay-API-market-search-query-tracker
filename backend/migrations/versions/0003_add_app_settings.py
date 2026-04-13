"""Add app_settings table for persistent user-configurable settings.

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-13 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("value", sa.Text, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("app_settings")
