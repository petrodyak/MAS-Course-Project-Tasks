from __future__ import annotations

import sqlite3

from .entity10_db_schema import ensure_entity10_table


def apply_entity10_migration(db_path: str) -> None:
    """Apply Entity10 schema to the given SQLite db path."""

    with sqlite3.connect(db_path) as conn:
        ensure_entity10_table(conn)
