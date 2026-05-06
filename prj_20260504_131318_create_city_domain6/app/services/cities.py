from __future__ import annotations

import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.city import City
from app.schemas.city import CityCreateRequest, CityUpdateRequest


def create_city(db: Session, payload: CityCreateRequest) -> City:
    now = dt.datetime.utcnow()
    city = City(
        city_name=payload.city_name,
        city_old_name=payload.city_old_name,
        city_size_km2=payload.city_size_km2,
        country=payload.country,
        established_date=payload.established_date,
        notes=payload.notes,
        created_at=now,
        updated_at=now,
    )
    db.add(city)
    db.commit()
    db.refresh(city)
    return city


def get_city(db: Session, city_id: int) -> City | None:
    return db.execute(select(City).where(City.city_id == city_id)).scalar_one_or_none()


def update_city(db: Session, city_id: int, payload: CityUpdateRequest) -> City | None:
    city = get_city(db, city_id)
    if city is None:
        return None

    city.city_name = payload.city_name
    city.city_old_name = payload.city_old_name
    city.city_size_km2 = payload.city_size_km2
    city.country = payload.country
    city.established_date = payload.established_date
    city.notes = payload.notes
    city.updated_at = dt.datetime.utcnow()

    db.commit()
    db.refresh(city)
    return city


def delete_city(db: Session, city_id: int) -> bool:
    city = get_city(db, city_id)
    if city is None:
        return False
    db.delete(city)
    db.commit()
    return True
