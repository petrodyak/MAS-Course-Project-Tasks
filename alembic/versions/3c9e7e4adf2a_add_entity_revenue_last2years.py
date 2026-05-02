"""add_entity_revenue_last2years

Revision ID: 3c9e7e4adf2a
Revises: 17fdcdd2f161
Create Date: 2026-04-30 14:10:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "3c9e7e4adf2a"
down_revision = "17fdcdd2f161"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "Entity6",
        sa.Column(
            "entity_revenue_last2years",
            sa.Float,
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("Entity6", "entity_revenue_last2years")
