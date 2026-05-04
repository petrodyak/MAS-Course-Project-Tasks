from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RoomCreate(BaseModel):
    room_name: str = Field(min_length=1, max_length=255)
    location: str = Field(min_length=1, max_length=255)
    room_capacity: int = Field(ge=0)


class RoomRead(RoomCreate):
    room_id: int
    created_at: datetime
    updated_at: datetime
