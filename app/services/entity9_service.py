from __future__ import annotations

import datetime as dt
from typing import Optional

from app.repositories.entity9_repository import (
    Entity9NotFoundError,
    Entity9Repository,
)


class Entity9Service:
    def __init__(self, db_path: str):
        self._repo = Entity9Repository(db_path)

    @staticmethod
    def _utc_now_iso() -> str:
        return dt.datetime.now(dt.timezone.utc).isoformat()

    def create_entity9(self, *, id: str, entity_name: str, entity_revenue: Optional[float]):
        now = self._utc_now_iso()
        # Let DB constraints raise on invalid entity_name.
        return self._repo.create(
            id=id,
            entity_name=entity_name,
            entity_revenue=entity_revenue,
            entity_creation_date=now,
            entity_updated_date=now,
        )

    def update_entity9(
        self,
        *,
        id: str,
        entity_name: str,
        entity_revenue: Optional[float],
    ):
        return self._repo.update(
            id=id,
            entity_name=entity_name,
            entity_revenue=entity_revenue,
        )

    def delete_entity9(self, *, id: str) -> None:
        self._repo.delete(id=id)

    def get_entity9(self, *, id: str):
        return self._repo.get_by_id(id=id)

    def list_entity9(self, *, limit: int = 100, offset: int = 0):
        return self._repo.list(limit=limit, offset=offset)


__all__ = ["Entity9Service", "Entity9NotFoundError"]
