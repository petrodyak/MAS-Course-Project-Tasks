from __future__ import annotations

# Placeholder for wiring into a real web framework.
# Current task focuses on DB + service layer and tests.

from app.services.entity9_service import Entity9NotFoundError, Entity9Service


def create_entity9_route(db_path: str, payload: dict):
    service = Entity9Service(db_path)
    return service.create_entity9(
        id=payload["id"],
        entity_name=payload["entity_name"],
        entity_revenue=payload.get("entity_revenue"),
    )


__all__ = ["create_entity9_route", "Entity9NotFoundError", "Entity9Service"]
