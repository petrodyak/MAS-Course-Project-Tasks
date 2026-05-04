from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ShelfCreate(BaseModel):
    shelf_name: str = Field(min_length=1, max_length=255)
    room_id: int
    shelf_capacity: int = Field(ge=0)


class ShelfRead(ShelfCreate):
    shelf_id: int
    created_at: datetime
    updated_at: datetime
