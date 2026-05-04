from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict


class CityBase(BaseModel):
    city_name: str
    city_old_name: str | None = None
    city_size_km2: float | None = None
    country: str | None = None
    established_date: dt.date | None = None
    notes: str | None = None


class CityCreateRequest(CityBase):
    city_name: str


class CityUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city_name: str
    city_old_name: str | None = None
    city_size_km2: float | None = None
    country: str | None = None
    established_date: dt.date | None = None
    notes: str | None = None


class CityRead(CityBase):
    city_id: int
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)
