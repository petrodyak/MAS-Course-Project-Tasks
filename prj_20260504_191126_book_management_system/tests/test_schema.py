from __future__ import annotations

import os
import sqlite3

import pytest

from app.setup import ensure_setup


def _apply_schema_sql(db_path: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rooms (
                room_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                room_name VARCHAR(255) NOT NULL,
                location VARCHAR(255) NOT NULL,
                room_capacity INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS shelves (
                shelf_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                shelf_name VARCHAR(255) NOT NULL,
                room_id INTEGER NOT NULL,
                shelf_capacity INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(room_id) REFERENCES rooms(room_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                book_title VARCHAR(500) NOT NULL,
                isbn VARCHAR(32) NOT NULL,
                author VARCHAR(255) NOT NULL,
                shelf_id INTEGER NOT NULL,
                published_date DATETIME,
                book_description TEXT,
                is_available BOOLEAN NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(shelf_id) REFERENCES shelves(shelf_id)
            )
            """
        )
        conn.commit()


def test_schema_column_names(conn, db_path):
    artifacts = os.path.join(os.path.dirname(db_path), "artifacts")
    ensure_setup(db_path, artifacts)
    cursor = conn.execute("PRAGMA table_info(rooms)")
    columns = {row["name"] for row in cursor.fetchall()}
    assert {"room_id", "room_name", "location", "room_capacity"}.issubset(columns)

    cursor = conn.execute("PRAGMA table_info(shelves)")
    columns = {row["name"] for row in cursor.fetchall()}
    assert {"shelf_id", "shelf_name", "room_id", "shelf_capacity"}.issubset(columns)

    cursor = conn.execute("PRAGMA table_info(books)")
    columns = {row["name"] for row in cursor.fetchall()}
    assert {"book_id", "book_title", "isbn", "author", "shelf_id", "is_available"}.issubset(columns)


def test_schema_column_types(conn, db_path):
    artifacts = os.path.join(os.path.dirname(db_path), "artifacts")
    ensure_setup(db_path, artifacts)

    types = {}
    cursor = conn.execute("PRAGMA table_info(rooms)")
    for row in cursor.fetchall():
        types[row["name"]] = row["type"].upper()
    assert types["room_id"] in {"INTEGER"}
    assert types["room_name"].startswith("VARCHAR")
    assert types["location"].startswith("VARCHAR")
    assert types["room_capacity"] in {"INTEGER"}


def test_migration_idempotent(tmp_path):
    import os
    import app.setup as setup_mod

    db = os.path.join(tmp_path, "data", "app.db")
    artifacts = os.path.join(tmp_path, "artifacts")
    os.makedirs(os.path.dirname(db), exist_ok=True)

    setup_mod.ensure_setup(db, artifacts)
    setup_mod.ensure_setup(db, artifacts)

    with sqlite3.connect(db) as conn:
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        ]
    assert "rooms" in tables
    assert "shelves" in tables
    assert "books" in tables
