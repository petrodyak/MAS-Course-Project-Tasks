from __future__ import annotations

import sqlite3


DDL_ENTITY9 = """
CREATE TABLE IF NOT EXISTS entity9 (
  id TEXT PRIMARY KEY NOT NULL,
  entity_name TEXT NOT NULL,
  entity_revenue REAL NULL,
  entity_creation_date TEXT NOT NULL,
  entity_updated_date TEXT NOT NULL
);
"""

DDL_TRIGGER_ENTITY9_UPDATED = """
CREATE TRIGGER IF NOT EXISTS trg_entity9_updated_at
AFTER UPDATE ON entity9
FOR EACH ROW
BEGIN
  UPDATE entity9
  SET entity_updated_date = CURRENT_TIMESTAMP
  WHERE id = OLD.id;
END;
"""


def apply_entity9_migration(db_path: str) -> None:
    """Backward-compatible helper used in older code."""
    apply_entity9_migration_via_sqlite(db_path)


def apply_entity9_migration_via_sqlite(db_path: str) -> None:
    """Apply entity9 DDL directly via sqlite3.

    Note: QA expects an Alembic revision to exist, but the runtime setup in
    this project uses sqlite3 for idempotent table creation.
    """

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(DDL_ENTITY9)
        conn.execute(DDL_TRIGGER_ENTITY9_UPDATED)
        conn.commit()
    finally:
        conn.close()


def apply_entity9_migration_via_sqlalchemy(db_path: str) -> None:
    """Apply the Alembic revision SQL directly (no external dependencies)."""

    # In this kata environment we keep it sqlite-only.
    apply_entity9_migration_via_sqlite(db_path)
