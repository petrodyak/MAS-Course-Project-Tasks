from __future__ import annotations

import sqlite3
from pathlib import Path

from app.db import ensure_db_schema

# Ensure tests and runtime always have SQLite FK enforcement.


def _ensure_businesses_table(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS businesses (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              type TEXT NOT NULL,
              city_id INTEGER NOT NULL,
              description TEXT NULL,
              established_year TEXT NULL,
              CONSTRAINT fk_businesses_city_id FOREIGN KEY(city_id) REFERENCES city(id) ON DELETE CASCADE
            );
            """
        )

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_businesses_city_id ON businesses(city_id);"
        )
        conn.commit()
    finally:
        conn.close()


def _ensure_district_table(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS district (
              district_id INTEGER PRIMARY KEY AUTOINCREMENT,
              city_id INTEGER NOT NULL,
              name TEXT NOT NULL,
              code TEXT NULL,
              type TEXT NOT NULL,
              status TEXT NOT NULL,
              CONSTRAINT fk_district_city FOREIGN KEY(city_id) REFERENCES city(id)
                ON DELETE RESTRICT ON UPDATE RESTRICT,
              CONSTRAINT chk_district_name_nonempty CHECK (length(trim(name)) > 0),
              CONSTRAINT chk_district_type CHECK (type IN ('urban','suburban','industrial','other')),
              CONSTRAINT chk_district_status CHECK (status IN ('active','merged','deprecated'))
            );
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_district_city_id ON district(city_id);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_district_status ON district(status);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_district_type ON district(type);"
        )
        conn.commit()
    finally:
        conn.close()


def _ensure_transport_system_tables(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transport_system (
              id INTEGER PRIMARY KEY,
              city_id INTEGER NOT NULL,
              name TEXT NOT NULL,
              transport_type TEXT NOT NULL,
              notes TEXT,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
              updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (city_id) REFERENCES city(id) ON DELETE CASCADE,
              UNIQUE (city_id, name, transport_type),
              CONSTRAINT chk_transport_type CHECK (transport_type IN ('Metro','Bus','Tram')),
              CONSTRAINT chk_transport_name_nonempty CHECK (length(trim(name)) > 0)
            );
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS station_stop (
              id INTEGER PRIMARY KEY,
              transport_system_id INTEGER NOT NULL,
              name TEXT NOT NULL,
              stop_type TEXT NOT NULL,
              code TEXT,
              address TEXT,
              order_index INTEGER,
              is_active BOOLEAN NOT NULL DEFAULT 1,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
              updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (transport_system_id) REFERENCES transport_system(id) ON DELETE CASCADE,
              UNIQUE (transport_system_id, code),
              CONSTRAINT chk_station_stop_type CHECK (stop_type IN ('Airport','Train Station','Stop')),
              CONSTRAINT chk_station_name_nonempty CHECK (length(trim(name)) > 0)
            );
            """
        )

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_transport_system_city_id ON transport_system(city_id);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_station_stop_transport_system_id ON station_stop(transport_system_id);"
        )

        conn.commit()
    finally:
        conn.close()


def ensure_setup(db_path: str, artifacts_path: str) -> None:
    """Idempotently ensure DB schema exists and write minimal artifacts."""

    Path(artifacts_path).mkdir(parents=True, exist_ok=True)
    ensure_db_schema(db_path)
    _ensure_district_table(db_path)
    _ensure_transport_system_tables(db_path)
    _ensure_businesses_table(db_path)

    marker = Path(artifacts_path) / "setup_complete.txt"
    marker.write_text(f"ok:{db_path}", encoding="utf-8")
