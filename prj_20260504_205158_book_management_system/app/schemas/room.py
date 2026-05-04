from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


class RoomBase(BaseModel):
    room_name: str = Field(max_length=255)
    room_description: str = Field(max_length=2000)


class RoomCreate(RoomBase):
    pass


class RoomUpdate(RoomBase):
    pass


class RoomRead(RoomBase):
    room_id: int
    created_at: datetime
    updated_at: datetime
