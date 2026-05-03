from __future__ import annotations

import sqlite3

from app.business_type import BusinessType


class BusinessRepositorySQLite:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        return {
            "id": row["id"],
            "name": row["name"],
            "type": row["type"],
            "city_id": row["city_id"],
            "description": row["description"],
            "established_year": row["established_year"],
        }

    def add_business(
        self,
        *,
        name: str,
        type: str,
        city_id: int,
        description: str | None = None,
        established_year: str | None = None,
    ) -> dict:
        if type not in BusinessType.values():
            raise ValueError(f"Invalid business type: {type}")

        conn = self._connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO businesses (name, type, city_id, description, established_year)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, type, city_id, description, established_year),
            )
            row = conn.execute(
                "SELECT * FROM businesses WHERE id = ?", (cur.lastrowid,)
            ).fetchone()
            if row is None:
                raise RuntimeError("Failed to insert business")
            conn.commit()
            return self._row_to_dict(row)
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def list_businesses_by_city(self, city_id: int) -> list[dict]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM businesses WHERE city_id = ? ORDER BY id", (city_id,)
            ).fetchall()
            return [self._row_to_dict(r) for r in rows]
        finally:
            conn.close()
