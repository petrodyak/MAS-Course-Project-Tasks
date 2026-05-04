from __future__ import annotations

import os
import sqlite3


def ensure_setup(db_path: str, artifacts_path: str) -> None:
    """Ensure the SQLite schema exists and is initialized idempotently."""

    db_path_abs = os.path.abspath(db_path)
    artifacts_path_abs = os.path.abspath(artifacts_path)

    os.makedirs(os.path.dirname(db_path_abs), exist_ok=True)
    os.makedirs(artifacts_path_abs, exist_ok=True)

    with sqlite3.connect(db_path_abs) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS city (
                city_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                city_name VARCHAR(255) NOT NULL,
                city_old_name VARCHAR(255),
                city_size_km2 FLOAT,
                country VARCHAR(255),
                established_date DATE,
                notes TEXT,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS ix_city_city_name ON city (city_name)"
        )
        conn.commit()
