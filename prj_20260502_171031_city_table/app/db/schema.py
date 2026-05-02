from __future__ import annotations

import sqlite3


def ensure_db_schema(db_path: str) -> None:
    """Ensure base schema for development/testing.

    This project keeps table creation logic here for initial bootstrap.
    Alembic migrations may be used additionally, but the schema must exist for
    tests to run from scratch.
    """

    conn = sqlite3.connect(db_path)
    # Ensure FK constraints are enforced in SQLite.
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS city (
              id INTEGER PRIMARY KEY,
              city_name TEXT NOT NULL,
              city_size_sq_km REAL,
              country TEXT,
              establishment_date DATE,
              notes TEXT,
              created_at DATETIME,
              updated_at DATETIME
            );
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_city_city_name ON city(city_name);"
        )
        conn.commit()
    finally:
        conn.close()
