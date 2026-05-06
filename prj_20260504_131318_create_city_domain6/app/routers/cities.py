from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.city import CityCreateRequest, CityRead, CityUpdateRequest
from app.services.cities import create_city, delete_city, get_city, update_city

router = APIRouter(prefix="/cities", tags=["cities"])


@router.post("", status_code=201, response_model=CityRead)
def create_city_endpoint(
    payload: CityCreateRequest, request: Request, db: Session = Depends(get_db)
):
    city = create_city(db, payload)
    return city


@router.get("/{city_id}", response_model=CityRead)
def get_city_endpoint(
    city_id: int, request: Request, db: Session = Depends(get_db)
):
    city = get_city(db, city_id)
    if city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
    return city


@router.put("/{city_id}", response_model=CityRead)
def update_city_endpoint(
    city_id: int,
    payload: CityUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    city = update_city(db, city_id, payload)
    if city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
    return city


@router.delete("/{city_id}", status_code=204)
def delete_city_endpoint(
    city_id: int, request: Request, db: Session = Depends(get_db)
):
    ok = delete_city(db, city_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
    return None
