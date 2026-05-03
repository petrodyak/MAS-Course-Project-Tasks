from __future__ import annotations

import os
import sqlite3
from pathlib import Path


def ensure_setup(db_path: str, artifacts_path: str) -> None:
    """Idempotently ensure the schema for this project.

    This implementation uses pure SQL executed via sqlite3 and enforces
    foreign keys for tests.
    """

    Path(artifacts_path).mkdir(parents=True, exist_ok=True)

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")

        # Cities table is expected to already exist per project baseline.
        # We only ensure District here.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS District (
                district_id TEXT NOT NULL PRIMARY KEY DEFAULT (lower(hex(randomblob(16))) || '-' || substr(lower(hex(randomblob(16))), 1, 4) || '-' || substr(lower(hex(randomblob(16))), 1, 4) || '-' || substr(lower(hex(randomblob(16))), 1, 4) || '-' || substr(lower(hex(randomblob(16))), 1, 12)),
                city_id      TEXT NOT NULL,
                name         TEXT NOT NULL,
                code         TEXT NULL,
                type         TEXT NOT NULL CHECK (type IN ('urban','suburban','industrial','rural')),
                status       TEXT NOT NULL CHECK (status IN ('active','merged','deprecated')),
                CONSTRAINT fk_district_city
                    FOREIGN KEY (city_id) REFERENCES cities(CityId) ON DELETE RESTRICT
            );
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_district_city_id ON District(city_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_district_status ON District(status);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_district_type ON District(type);")

        conn.commit()
    finally:
        conn.close()

    marker = Path(artifacts_path) / "setup_complete.txt"
    marker.write_text(f"ok:{db_path}", encoding="utf-8")
