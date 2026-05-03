from __future__ import annotations

from app.business_repository_sqlite import BusinessRepositorySQLite


class BusinessService:
    def __init__(self, repo: BusinessRepositorySQLite):
        self.repo = repo

    def create_business(
        self,
        *,
        name: str,
        type: str,
        city_id: int,
        description: str | None = None,
        established_year: str | None = None,
    ) -> dict:
        return self.repo.add_business(
            name=name,
            type=type,
            city_id=city_id,
            description=description,
            established_year=established_year,
        )

    def list_businesses_for_city(self, city_id: int) -> list[dict]:
        return self.repo.list_businesses_by_city(city_id)
