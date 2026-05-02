from __future__ import annotations

from typing import Any, Dict, Optional

from .entity10_repository import Entity10Repository


def _to_iso(dt_value: str) -> str:
    # Stored in SQLite as CURRENT_TIMESTAMP => "YYYY-MM-DD HH:MM:SS".
    # Keep as-is; tests validate existence and trigger update behavior.
    return dt_value


def create_entity10(
    repo: Entity10Repository, payload: Dict[str, Any]
) -> Dict[str, Any]:
    entity_name = payload.get("entityName")
    if entity_name is None:
        raise ValueError("entityName is required")

    entity_revenue: Optional[float] = payload.get("entityRevenue")

    # Scaffold: repository generates UUID for now.
    row = repo.create(entity_name=entity_name, entity_revenue=entity_revenue)
    return {"entityId": row.entity_id}


def get_entity10(repo: Entity10Repository, entity_id: str) -> Dict[str, Any]:
    row = repo.get_by_id(entity_id)
    if row is None:
        raise KeyError("not found")

    return {
        "entityId": row.entity_id,
        "entityName": row.entity_name,
        "entityRevenue": row.entity_revenue,
        "entityCreationDate": _to_iso(row.entity_creation_date),
        "entityUpdatedDate": _to_iso(row.entity_updated_date),
    }


def update_entity10(
    repo: Entity10Repository, entity_id: str, payload: Dict[str, Any]
) -> None:
    entity_name = payload.get("entityName")
    if entity_name is None:
        raise ValueError("entityName cannot be null")

    entity_revenue = payload.get("entityRevenue")
    ok = repo.update(
        entity_id, entity_name=entity_name, entity_revenue=entity_revenue
    )
    if not ok:
        raise KeyError("not found")


def delete_entity10(repo: Entity10Repository, entity_id: str) -> None:
    ok = repo.delete(entity_id)
    if not ok:
        raise KeyError("not found")
