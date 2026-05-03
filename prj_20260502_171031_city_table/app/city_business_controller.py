from __future__ import annotations

from app.business_repository_sqlite import BusinessRepositorySQLite
from app.business_service import BusinessService


class CityBusinessController:
    def __init__(self, db_path: str):
        self.service = BusinessService(BusinessRepositorySQLite(db_path))

    def post_business_for_city(
        self,
        *,
        city_id: int,
        name: str,
        type: str,
        description: str | None = None,
        established_year: str | None = None,
    ) -> dict:
        return self.service.create_business(
            name=name,
            type=type,
            city_id=city_id,
            description=description,
            established_year=established_year,
        )

    def get_businesses_for_city(self, city_id: int) -> list[dict]:
        return self.service.list_businesses_for_city(city_id)
