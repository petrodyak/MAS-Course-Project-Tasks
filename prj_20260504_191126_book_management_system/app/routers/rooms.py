from __future__ import annotations

import sqlite3
from fastapi import APIRouter, HTTPException, Request

from app.schemas.room import RoomCreate, RoomRead
from app.services.rooms import RoomsService

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("", status_code=201, response_model=RoomRead)
async def create_room(payload: RoomCreate, request: Request):
    service = RoomsService(request.app.state.db_path)
    try:
        return service.create(payload)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Integrity error")


@router.delete(
    "/{room_id}",
    status_code=204,
)
async def delete_room(room_id: int, request: Request):
    service = RoomsService(request.app.state.db_path)
    try:
        service.delete(room_id)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Deletion prevented")
    return None
