from __future__ import annotations

import sqlite3
from fastapi import APIRouter, HTTPException, Request

from app.schemas.shelf import ShelfCreate, ShelfRead
from app.services.shelves import ShelvesService

router = APIRouter(prefix="/shelves", tags=["shelves"])


@router.post("", status_code=201, response_model=ShelfRead)
async def create_shelf(payload: ShelfCreate, request: Request):
    service = ShelvesService(request.app.state.db_path)
    try:
        return service.create(payload)
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=404, detail="Referenced room not found")


@router.delete(
    "/{shelf_id}",
    status_code=204,
)
async def delete_shelf(shelf_id: int, request: Request):
    service = ShelvesService(request.app.state.db_path)
    try:
        service.delete(shelf_id)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Deletion prevented")
    return None
