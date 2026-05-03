from __future__ import annotations

import sqlite3
import uuid

import pytest

from app.setup import ensure_setup


def _create_city(conn: sqlite3.Connection, city_id: int = 1) -> None:
    # City baseline in real DB uses table cities with columns CityId/CityName.
    # But spec asks FK to City(city_id). To make tests meaningful with this
    # project baseline, we create a compatible City table in the temp db.
    # District FK references the project's Cities table. For temp-db tests
    # we create a compatible Cities schema.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cities (
            CityId INTEGER PRIMARY KEY,
            CityName TEXT NOT NULL
        );
        """
    )
    conn.execute(
        "INSERT OR IGNORE INTO cities (CityId, CityName) VALUES (?, ?)",
        (city_id, "Kyiv"),
    )


def _district_row(
    district_id: str,
    city_id: int,
    name: str,
    code: str | None,
    type_: str,
    status: str,
) -> tuple:
    return (district_id, city_id, name, code, type_, status)


def test_schema_column_names(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    artifacts = str(tmp_path / "artifacts")

    # Ensure City table exists for FK validation.
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        _create_city(conn)
        conn.commit()
    finally:
        conn.close()

    ensure_setup(db_path, artifacts)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cols = {
            r["name"]
            for r in conn.execute("PRAGMA table_info(District)").fetchall()
        }
        expected = {"district_id", "city_id", "name", "code", "type", "status"}
        assert expected.issubset(cols)
    finally:
        conn.close()


def test_schema_column_types(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    artifacts = str(tmp_path / "artifacts")

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        _create_city(conn)
        conn.commit()
    finally:
        conn.close()

    ensure_setup(db_path, artifacts)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        types = {
            r["name"]: str(r["type"]).upper()
            for r in conn.execute("PRAGMA table_info(District)").fetchall()
        }
        assert types["district_id"].startswith("TEXT")
        assert types["city_id"].startswith("TEXT")
        assert types["name"].startswith("TEXT")
        assert types["code"].startswith("TEXT") or ""  # nullable
        assert types["type"].startswith("TEXT")
        assert types["status"].startswith("TEXT")
    finally:
        conn.close()


def test_migration_idempotent(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    artifacts = str(tmp_path / "artifacts")

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        _create_city(conn)
        conn.commit()
    finally:
        conn.close()

    ensure_setup(db_path, artifacts)
    ensure_setup(db_path, artifacts)

    conn = sqlite3.connect(db_path)
    try:
        tables = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert "District" in tables
    finally:
        conn.close()


def test_fk_orphan_insert_rejected(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    artifacts = str(tmp_path / "artifacts")

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        _create_city(conn)
        conn.commit()
    finally:
        conn.close()

    ensure_setup(db_path, artifacts)

    district_id = str(uuid.uuid4())
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO District (district_id, city_id, name, code, type, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                _district_row(
                    district_id,
                    999,
                    "Ghost District",
                    None,
                    "urban",
                    "active",
                ),
            )
        conn.rollback()
    finally:
        conn.close()


def test_positive_active_insert_succeeds(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    artifacts = str(tmp_path / "artifacts")

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        _create_city(conn, city_id=1)
        conn.commit()
    finally:
        conn.close()

    ensure_setup(db_path, artifacts)

    district_id = str(uuid.uuid4())
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute(
            """
            INSERT INTO District (district_id, city_id, name, code, type, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            _district_row(
                district_id,
                1,
                "Shevchenkivskyi District",
                "KV-SHV",
                "urban",
                "active",
            ),
        )
        row = conn.execute(
            "SELECT city_id, name, code, type, status FROM District WHERE district_id = ?",
            (district_id,),
        ).fetchone()
        assert row is not None
        assert str(row[0]) == "1"
        assert row[1] == "Shevchenkivskyi District"
        assert row[2] == "KV-SHV"
        assert row[3] == "urban"
        assert row[4] == "active"
    finally:
        conn.close()


def test_status_check_rejects_unknown(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    artifacts = str(tmp_path / "artifacts")

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        _create_city(conn, city_id=1)
        conn.commit()
    finally:
        conn.close()

    ensure_setup(db_path, artifacts)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO District (district_id, city_id, name, code, type, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                _district_row(
                    str(uuid.uuid4()),
                    1,
                    "BadStatusDistrict",
                    None,
                    "urban",
                    "unknown",
                ),
            )
        conn.rollback()
    finally:
        conn.close()


def test_name_not_null(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    artifacts = str(tmp_path / "artifacts")

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        _create_city(conn, city_id=1)
        conn.commit()
    finally:
        conn.close()

    ensure_setup(db_path, artifacts)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO District (district_id, city_id, name, code, type, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                _district_row(
                    str(uuid.uuid4()),
                    1,
                    None,
                    None,
                    "urban",
                    "active",
                ),
            )
        conn.rollback()
    finally:
        conn.close()
