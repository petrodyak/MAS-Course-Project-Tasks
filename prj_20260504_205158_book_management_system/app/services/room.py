from __future__ import annotations
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.room import Room


def delete_room(db: Session, room_id: int) -> None:
    shelves_count = db.execute(
        text("SELECT COUNT(1) FROM shelves WHERE room_id = :room_id"),
        {"room_id": room_id},
    ).scalar_one()
    if shelves_count:
        raise ValueError("Deletion rejected due to existing shelves")
    room = db.get(Room, room_id)
    if not room:
        raise KeyError("Room not found")
    db.delete(room)
