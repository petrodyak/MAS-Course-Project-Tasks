from __future__ import annotations

import datetime as dt
import sqlite3

import pytest

from app.setup import ensure_setup


def _table_columns(conn: sqlite3.Connection, table: str) -> dict[str, str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {r["name"]: (r["type"] or "").upper() for r in rows}


def test_schema_column_names_and_types(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    ensure_setup(db_path, str(tmp_path / "art"))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cols = _table_columns(conn, "city")
        assert "id" in cols
        assert "city_name" in cols
        assert "city_size_sq_km" in cols
        assert "country" in cols
        assert "establishment_date" in cols
        assert "notes" in cols
        assert "created_at" in cols
        assert "updated_at" in cols

        # basic type expectations
        assert cols["id"] == "INTEGER"
        assert "TEXT" in cols["city_name"]
    finally:
        conn.close()


def test_city_name_not_null_constraint(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    ensure_setup(db_path, str(tmp_path / "art"))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO city (city_name) VALUES (?)",
                (None,),
            )
        conn.rollback()
    finally:
        conn.close()


def test_crud_update_delete(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    ensure_setup(db_path, str(tmp_path / "art"))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        now = dt.datetime.utcnow().isoformat()
        cur = conn.execute(
            """
            INSERT INTO city (city_name, city_size_sq_km, country, establishment_date, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "Kyiv",
                840.0,
                "Ukraine",
                "1982-01-01",
                "big city",
                now,
                now,
            ),
        )
        city_id = cur.lastrowid

        row = conn.execute("SELECT * FROM city WHERE id = ?", (city_id,)).fetchone()
        assert row["city_name"] == "Kyiv"

        conn.execute(
            "UPDATE city SET city_size_sq_km = ?, updated_at = ? WHERE id = ?",
            (900.0, now, city_id),
        )
        row2 = conn.execute("SELECT * FROM city WHERE id = ?", (city_id,)).fetchone()
        assert row2["city_size_sq_km"] == 900.0

        conn.execute("DELETE FROM city WHERE id = ?", (city_id,))
        remaining = conn.execute("SELECT * FROM city").fetchall()
        assert remaining == []

    finally:
        conn.close()
