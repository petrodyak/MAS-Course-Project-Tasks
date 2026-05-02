from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest


EXPECTED_COLUMNS = {
    "Entity6Id",
    "entity_name",
    "entity_revenue",
    "entity_revenue_last2years",
    "entity_creation_date",
    "entity_updated_date",
    "created_by",
    "updated_by",
    "import_source",
    "external_reference",
    "notes",
    "is_deleted",
}


def test_ensure_setup_self_heals_incomplete_schema(tmp_path: Path):
    from app.setup import ensure_setup

    db_path = tmp_path / "incomplete.db"
    artifacts = tmp_path / "artifacts"

    # Pre-seed an incomplete Entity6 table missing entity_revenue_last2years.
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            CREATE TABLE Entity6 (
                Entity6Id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT NOT NULL,
                entity_revenue FLOAT NOT NULL,
                entity_creation_date TEXT NOT NULL,
                entity_updated_date TEXT NOT NULL,
                created_by TEXT,
                updated_by TEXT,
                import_source TEXT,
                external_reference TEXT,
                notes TEXT,
                is_deleted INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()
    finally:
        conn.close()

    ensure_setup(str(db_path), str(artifacts))

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute("PRAGMA table_info('Entity6')")
        cols = {r["name"] for r in cur.fetchall()}
        assert EXPECTED_COLUMNS.issubset(cols)
    finally:
        conn.close()
