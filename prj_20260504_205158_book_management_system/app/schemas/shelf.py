from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


class ShelfBase(BaseModel):
    shelf_name: str = Field(max_length=255)
    shelf_code: str = Field(max_length=255)
    shelf_description: str = Field(max_length=2000)
    room_id: int


class ShelfCreate(ShelfBase):
    pass


class ShelfUpdate(ShelfBase):
    pass


class ShelfRead(ShelfBase):
    shelf_id: int
    created_at: datetime
    updated_at: datetime
