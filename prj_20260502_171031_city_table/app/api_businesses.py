from __future__ import annotations

from app.city_business_controller import CityBusinessController


def create_business_endpoint(db_path: str) -> CityBusinessController:
    return CityBusinessController(db_path)
