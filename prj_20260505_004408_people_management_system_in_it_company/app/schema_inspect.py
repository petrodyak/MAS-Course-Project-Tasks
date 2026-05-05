from __future__ import annotations
import sqlite3


def get_schema(db_path: str) -> dict[str, list[str]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
        ]
        schema: dict[str, list[str]] = {}
        for t in tables:
            cols = [
                row["name"]
                for row in conn.execute(f"PRAGMA table_info({t})").fetchall()
            ]
            schema[t] = cols
        return schema
    finally:
        conn.close()
