from __future__ import annotations

from alembic import op


# revision identifiers, used by Alembic.
revision = "0001_create_entity9_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS entity9 (
          id TEXT PRIMARY KEY NOT NULL,
          entity_name TEXT NOT NULL,
          entity_revenue REAL NULL,
          entity_creation_date TEXT NOT NULL,
          entity_updated_date TEXT NOT NULL
        );
        """
    )

    # Keep entity_updated_date in sync on update.
    op.execute(
        """
        CREATE TRIGGER IF NOT EXISTS trg_entity9_updated_at
        AFTER UPDATE ON entity9
        FOR EACH ROW
        BEGIN
          UPDATE entity9
          SET entity_updated_date = CURRENT_TIMESTAMP
          WHERE id = OLD.id;
        END;
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_entity9_updated_at;")
    op.execute("DROP TABLE IF EXISTS entity9;")
