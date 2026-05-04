from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models.shelf import Shelf
from app.models.room import Room
from app.schemas.book import BookRead
from app.schemas.shelf import ShelfCreate, ShelfRead, ShelfUpdate

router = APIRouter(prefix="/shelves", tags=["shelves"])


@router.get("")
def list_shelves(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    shelves = db.query(Shelf).order_by(Shelf.shelf_id.asc()).all()
    items = [ShelfRead.model_validate(s, from_attributes=True).model_dump() for s in shelves]
    return {"items": items}


@router.post("", status_code=201, response_model=ShelfRead)
def create_shelf(
    payload: ShelfCreate,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    room = db.get(Room, payload.room_id)
    if not room:
        raise HTTPException(status_code=400, detail="Invalid room_id")

    shelf = Shelf(
        shelf_name=payload.shelf_name,
        shelf_code=payload.shelf_code,
        shelf_description=payload.shelf_description,
        room_id=payload.room_id,
    )
    db.add(shelf)
    db.commit()
    db.refresh(shelf)
    return shelf


@router.get("/{shelf_id}", response_model=ShelfRead)
def get_shelf(
    shelf_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    shelf = db.get(Shelf, shelf_id)
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")
    return shelf


@router.put("/{shelf_id}", response_model=ShelfRead)
def update_shelf(
    shelf_id: int,
    payload: ShelfUpdate,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    shelf = db.get(Shelf, shelf_id)
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")

    room = db.get(Room, payload.room_id)
    if not room:
        raise HTTPException(status_code=400, detail="Invalid room_id")

    shelf.shelf_name = payload.shelf_name
    shelf.shelf_code = payload.shelf_code
    shelf.shelf_description = payload.shelf_description
    shelf.room_id = payload.room_id

    db.commit()
    db.refresh(shelf)
    return shelf


@router.delete("/{shelf_id}", status_code=204)
def delete_shelf(
    shelf_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    from app.services.shelf import delete_shelf as svc_delete_shelf

    try:
        svc_delete_shelf(db, shelf_id)
        db.commit()
    except KeyError:
        raise HTTPException(status_code=404, detail="Shelf not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return None


@router.get("/{shelf_id}/books")
def list_books_in_shelf(
    shelf_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    shelf = db.get(Shelf, shelf_id)
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")
    from app.models.book import Book

    books = (
        db.query(Book).filter(Book.shelf_id == shelf_id).order_by(Book.book_id.asc()).all()
    )
    items = [BookRead.model_validate(b, from_attributes=True).model_dump() for b in books]
    return {"items": items}
