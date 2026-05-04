from __future__ import annotations

import os
import sqlite3

import pytest


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "data" / "app.db")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def test_schema_column_names_and_types(tmp_path, db_path):
    from app.setup import ensure_setup

    ensure_setup(db_path, str(tmp_path / "artifacts"))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # column names
    cursor = conn.execute("PRAGMA table_info(rooms)")
    columns = {row["name"] for row in cursor.fetchall()}
    assert {"room_id", "room_name", "location", "room_capacity", "created_at", "updated_at"}.issubset(columns)

    # types
    cursor = conn.execute("PRAGMA table_info(rooms)")
    types = {row["name"]: row["type"].upper() for row in cursor.fetchall()}
    assert types["room_id"] == "INTEGER"
    assert "VARCHAR" in types["room_name"]

    cursor = conn.execute("PRAGMA table_info(shelves)")
    columns = {row["name"] for row in cursor.fetchall()}
    assert {"shelf_id", "shelf_name", "room_id", "shelf_capacity"}.issubset(columns)

    cursor = conn.execute("PRAGMA table_info(books)")
    columns = {row["name"] for row in cursor.fetchall()}
    assert {"book_id", "book_title", "isbn", "author", "shelf_id", "is_available"}.issubset(columns)

    conn.close()


def test_migration_idempotent(source_path=None):
    # Alembic is verified by applying migrations once/twice via helper import
    import sys

    source_root = os.environ.get(
        "BOOK_SOURCE_PATH"
    )
    if not source_root:
        # best-effort fallback: tests executed from repo root where source is cwd
        source_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    sys.path.insert(0, source_root)

    from app.setup import ensure_setup

    db = os.path.join(source_root, "data", "app.db")
    artifacts = os.path.join(source_root, "artifacts")
    os.makedirs(os.path.dirname(db), exist_ok=True)
    ensure_setup(db, artifacts)
    # calling twice must not raise
    ensure_setup(db, artifacts)

    conn = sqlite3.connect(db)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    conn.close()
    assert "rooms" in tables
    assert "shelves" in tables
    assert "books" in tables
