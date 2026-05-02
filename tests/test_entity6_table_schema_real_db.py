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


def _table_info(conn: sqlite3.Connection, table: str) -> set[str]:
    conn.row_factory = sqlite3.Row
    cur = conn.execute(f"PRAGMA table_info('{table}')")
    rows = cur.fetchall()
    return {r["name"] for r in rows}


def test_project_database_has_expected_columns_for_Entity6(tmp_path: Path):
    # Target the real project DB under data/app.db
    project_root = Path(__file__).resolve().parents[1]
    db_path = project_root / "data" / "app.db"
    artifacts_path = project_root / "artifacts"

    from app.setup import ensure_setup

    ensure_setup(str(db_path), str(artifacts_path))

    conn = sqlite3.connect(str(db_path))
    try:
        cols = _table_info(conn, "Entity6")
        assert EXPECTED_COLUMNS.issubset(cols)
    finally:
        conn.close()
