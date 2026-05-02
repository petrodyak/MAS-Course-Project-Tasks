from __future__ import annotations

import sqlite3
import pytest

from app.setup import ensure_setup


def test_district_table_exists(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    ensure_setup(db_path, str(tmp_path / "artifacts"))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        tables = {r["name"] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        assert "district" in tables

        cols = {r["name"] for r in conn.execute("PRAGMA table_info(district)").fetchall()}
        expected = {
            "district_id",
            "city_id",
            "name",
            "code",
            "type",
            "status",
        }
        assert expected.issubset(cols)
    finally:
        conn.close()


def test_fk_orphan_insert_rejected(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    ensure_setup(db_path, str(tmp_path / "artifacts"))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO district (city_id, name, code, type, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    99999,  # no such city(id)
                    "Shevchenkivskyi District",
                    None,
                    "urban",
                    "active",
                ),
            )
        conn.rollback()
    finally:
        conn.close()


@pytest.mark.parametrize(
    "name, type_, status_",
    [
        ("", "urban", "active"),
        ("   ", "urban", "active"),
        ("Some District", "invalid_type", "active"),
        ("Some District", "urban", "invalid_status"),
    ],
)
def test_checks_reject_invalid_values(tmp_path, name, type_, status_):
    db_path = str(tmp_path / "db.sqlite")
    ensure_setup(db_path, str(tmp_path / "artifacts"))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        # create a valid city(id)
        cur = conn.execute("INSERT INTO city (city_name) VALUES (?)", ("Kyiv",))
        city_id = cur.lastrowid

        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO district (city_id, name, code, type, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (city_id, name, None, type_, status_),
            )
        conn.rollback()
    finally:
        conn.close()
