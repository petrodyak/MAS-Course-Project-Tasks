from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any

from app.db import connect
from app.schemas.room import RoomCreate


@dataclass(frozen=True)
class RoomsService:
    db_path: str

    def create(self, payload: RoomCreate) -> dict[str, Any]:
        with connect(self.db_path) as conn:
            cur = conn.execute(
                """
                INSERT INTO rooms (room_name, location, room_capacity)
                VALUES (?, ?, ?)
                """,
                (payload.room_name, payload.location, payload.room_capacity),
            )
            room_id = cur.lastrowid
            row = conn.execute(
                "SELECT room_id, room_name, location, room_capacity, created_at, updated_at FROM rooms WHERE room_id = ?",
                (room_id,),
            ).fetchone()
            return {
                "room_id": row[0],
                "room_name": row[1],
                "location": row[2],
                "room_capacity": row[3],
                "created_at": row[4],
                "updated_at": row[5],
            }

    def delete(self, room_id: int) -> None:
        with connect(self.db_path) as conn:
            try:
                conn.execute("DELETE FROM rooms WHERE room_id = ?", (room_id,))
            except sqlite3.IntegrityError as e:
                raise sqlite3.IntegrityError("ROOM_DELETION_CONFLICT") from e
