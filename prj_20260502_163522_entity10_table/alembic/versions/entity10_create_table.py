"""entity10 create table

Revision ID: e10a1b2c3d4e
Revises:
Create Date: 2026-05-02

This revision is deterministic and idempotent for SQLite.
"""

from __future__ import annotations

from alembic import op

revision = "e10a1b2c3d4e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS entity10 (
            entity_id TEXT PRIMARY KEY NOT NULL,
            entity_name TEXT NOT NULL,
            entity_revenue REAL NULL,
            entity_creation_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            entity_updated_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TRIGGER IF NOT EXISTS entity10_updated_at
        AFTER UPDATE ON entity10
        FOR EACH ROW
        BEGIN
            UPDATE entity10
            SET entity_updated_date = CURRENT_TIMESTAMP
            WHERE entity_id = OLD.entity_id;
        END;
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS entity10_updated_at;")
    op.execute("DROP TABLE IF EXISTS entity10;")
