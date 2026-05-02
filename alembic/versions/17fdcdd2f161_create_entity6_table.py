"""create_entity6_table

Revision ID: 17fdcdd2f161
Revises:
Create Date: 2026-04-30 14:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "17fdcdd2f161"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "Entity6",
        sa.Column("Entity6Id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("entity_name", sa.String, nullable=False),
        sa.Column("entity_revenue", sa.Float, nullable=False),
        sa.Column("entity_creation_date", sa.DateTime, nullable=False),
        sa.Column("entity_updated_date", sa.DateTime, nullable=False),
        sa.Column("created_by", sa.String, nullable=True),
        sa.Column("updated_by", sa.String, nullable=True),
        sa.Column("import_source", sa.String, nullable=True),
        sa.Column("external_reference", sa.String, nullable=True, unique=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_deleted", sa.Integer, nullable=False, server_default="0"),
        sa.CheckConstraint("entity_revenue = entity_revenue", name="ck_entity6_revenue_not_nan"),
        sa.CheckConstraint("trim(entity_name) <> ''", name="ck_entity6_name_not_blank"),
        sa.CheckConstraint("is_deleted IN (0, 1)", name="ck_entity6_is_deleted_bool"),
    )
    op.create_index(
        "uq_entity6_external_reference",
        "Entity6",
        ["external_reference"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_entity6_external_reference", table_name="Entity6")
    op.drop_table("Entity6")
