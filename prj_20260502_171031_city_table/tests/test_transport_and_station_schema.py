from __future__ import annotations

import sqlite3
import pytest

from app.setup import ensure_setup


def _fetch_fk_list(conn: sqlite3.Connection, table: str) -> list[dict]:
    rows = conn.execute(f"PRAGMA foreign_key_list({table})").fetchall()
    out: list[dict] = []
    for r in rows:
        out.append({
            "id": r["id"],
            "seq": r["seq"],
            "table": r["table"],
            "from": r["from"],
            "to": r["to"],
            "on_update": r["on_update"],
            "on_delete": r["on_delete"],
        })
    return out


def test_schema_creates_transport_tables(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    ensure_setup(db_path, str(tmp_path / "art"))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        tables = {r["name"] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        assert "transport_system" in tables
        assert "station_stop" in tables

        cols_ts = {r["name"] for r in conn.execute(
            "PRAGMA table_info(transport_system)"
        ).fetchall()}
        assert {"id", "city_id", "name", "transport_type", "notes"}.issubset(
            cols_ts
        )

        cols_ss = {r["name"] for r in conn.execute(
            "PRAGMA table_info(station_stop)"
        ).fetchall()}
        assert {"id", "transport_system_id", "name", "stop_type", "code"}.issubset(
            cols_ss
        )

        fk_transport = _fetch_fk_list(conn, "transport_system")
        assert len(fk_transport) == 1
        assert fk_transport[0]["table"] == "city"
        assert fk_transport[0]["on_delete"].upper() == "CASCADE"

        fk_station = _fetch_fk_list(conn, "station_stop")
        assert len(fk_station) == 1
        assert fk_station[0]["table"] == "transport_system"
        assert fk_station[0]["on_delete"].upper() == "CASCADE"

        # Ensure FK enforcement is enabled for this connection.
        conn.execute("PRAGMA foreign_keys = ON;")
        fk_prag = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        assert fk_prag == 1

    finally:
        conn.close()


def test_no_orphan_transport_system(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    ensure_setup(db_path, str(tmp_path / "art"))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO transport_system (city_id, name, transport_type)
                VALUES (?, ?, ?)
                """,
                (99999, "Main", "Metro"),
            )
        conn.rollback()
    finally:
        conn.close()


def test_no_orphan_station_stop(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    ensure_setup(db_path, str(tmp_path / "art"))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO station_stop (transport_system_id, name, stop_type)
                VALUES (?, ?, ?)
                """,
                (99999, "Central Airport", "Airport"),
            )
        conn.rollback()
    finally:
        conn.close()


def test_cascade_delete_city_removes_deps(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    ensure_setup(db_path, str(tmp_path / "art"))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        city_id = conn.execute(
            "INSERT INTO city (city_name) VALUES (?)", ("Kyiv",)
        ).lastrowid

        ts_id = conn.execute(
            """
            INSERT INTO transport_system (city_id, name, transport_type)
            VALUES (?, ?, ?)
            """,
            (city_id, "Metro Line 1", "Metro"),
        ).lastrowid

        conn.execute(
            """
            INSERT INTO station_stop (transport_system_id, name, stop_type)
            VALUES (?, ?, ?)
            """,
            (ts_id, "Central Station", "Train Station"),
        )

        conn.execute("DELETE FROM city WHERE id = ?", (city_id,))

        assert conn.execute("SELECT * FROM transport_system").fetchall() == []
        assert conn.execute("SELECT * FROM station_stop").fetchall() == []

    finally:
        conn.close()


def test_cascade_delete_transport_system_removes_stations(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    ensure_setup(db_path, str(tmp_path / "art"))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        city_id = conn.execute(
            "INSERT INTO city (city_name) VALUES (?)", ("Kyiv",)
        ).lastrowid
        ts_id = conn.execute(
            """
            INSERT INTO transport_system (city_id, name, transport_type)
            VALUES (?, ?, ?)
            """,
            (city_id, "Bus System", "Bus"),
        ).lastrowid
        conn.execute(
            """
            INSERT INTO station_stop (transport_system_id, name, stop_type)
            VALUES (?, ?, ?)
            """,
            (ts_id, "Stop A", "Stop"),
        )

        conn.execute("DELETE FROM transport_system WHERE id = ?", (ts_id,))
        assert conn.execute("SELECT * FROM station_stop").fetchall() == []

    finally:
        conn.close()


@pytest.mark.parametrize(
    "transport_type",
    ["", "invalid", "metro", None],
)
def test_transport_type_check_constraint(tmp_path, transport_type):
    if transport_type is None:
        pytest.skip("SQLite CHECK tests with NULL are driver/constraint dependent")

    db_path = str(tmp_path / "db.sqlite")
    ensure_setup(db_path, str(tmp_path / "art"))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        city_id = conn.execute(
            "INSERT INTO city (city_name) VALUES (?)", ("Kyiv",)
        ).lastrowid

        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO transport_system (city_id, name, transport_type)
                VALUES (?, ?, ?)
                """,
                (city_id, "Main", transport_type),
            )
        conn.rollback()
    finally:
        conn.close()

