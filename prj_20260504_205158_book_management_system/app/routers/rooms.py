from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomRead, RoomUpdate
from app.schemas.shelf import ShelfRead

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomRead])
def list_rooms(
    request: Request, db: Session = Depends(get_db), _: str = Depends(get_current_user)
):
    rooms = db.query(Room).order_by(Room.room_id.asc()).all()
    return rooms


@router.post("", status_code=201, response_model=RoomRead)
def create_room(
    payload: RoomCreate,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    room = Room(room_name=payload.room_name, room_description=payload.room_description)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.get("/{room_id}", response_model=RoomRead)
def get_room(
    room_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.put("/{room_id}", response_model=RoomRead)
def update_room(
    room_id: int,
    payload: RoomUpdate,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    room.room_name = payload.room_name
    room.room_description = payload.room_description
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=204)
def delete_room(
    room_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    from app.services.room import delete_room as svc_delete_room

    try:
        svc_delete_room(db, room_id)
        db.commit()
    except KeyError:
        raise HTTPException(status_code=404, detail="Room not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return None


@router.get("/{room_id}/shelves")
def list_shelves_in_room(
    room_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    from app.models.shelf import Shelf

    shelves = (
        db.query(Shelf).filter(Shelf.room_id == room_id).order_by(Shelf.shelf_id.asc()).all()
    )
    items = [ShelfRead.model_validate(s, from_attributes=True).model_dump() for s in shelves]
    return {"items": items}
