from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any

from app.db import connect
from app.schemas.shelf import ShelfCreate


@dataclass(frozen=True)
class ShelvesService:
    db_path: str

    def create(self, payload: ShelfCreate) -> dict[str, Any]:
        with connect(self.db_path) as conn:
            cur = conn.execute(
                """
                INSERT INTO shelves (shelf_name, room_id, shelf_capacity)
                VALUES (?, ?, ?)
                """,
                (payload.shelf_name, payload.room_id, payload.shelf_capacity),
            )
            shelf_id = cur.lastrowid
            row = conn.execute(
                "SELECT shelf_id, shelf_name, room_id, shelf_capacity, created_at, updated_at FROM shelves WHERE shelf_id = ?",
                (shelf_id,),
            ).fetchone()
            return {
                "shelf_id": row[0],
                "shelf_name": row[1],
                "room_id": row[2],
                "shelf_capacity": row[3],
                "created_at": row[4],
                "updated_at": row[5],
            }

    def delete(self, shelf_id: int) -> None:
        with connect(self.db_path) as conn:
            try:
                conn.execute("DELETE FROM shelves WHERE shelf_id = ?", (shelf_id,))
            except sqlite3.IntegrityError as e:
                raise sqlite3.IntegrityError("SHELF_DELETION_CONFLICT") from e
