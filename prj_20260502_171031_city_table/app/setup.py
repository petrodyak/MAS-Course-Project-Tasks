from __future__ import annotations

import sqlite3
from pathlib import Path

from app.db import ensure_db_schema

# Ensure tests and runtime always have SQLite FK enforcement.


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


def ensure_setup(db_path: str, artifacts_path: str) -> None:
    """Idempotently ensure DB schema exists and write minimal artifacts."""

    Path(artifacts_path).mkdir(parents=True, exist_ok=True)
    ensure_db_schema(db_path)
    _ensure_district_table(db_path)

    marker = Path(artifacts_path) / "setup_complete.txt"
    marker.write_text(f"ok:{db_path}", encoding="utf-8")
