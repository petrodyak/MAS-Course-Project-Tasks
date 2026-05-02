from __future__ import annotations

import math
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


@dataclass
class NotFoundError(Exception):
    entity6_id: int


def _now_utc_iso() -> datetime:
    return datetime.now(timezone.utc)


def _parse_db_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if value is None:
        raise ValueError("datetime value is None")
    # SQLite default may store as ISO-8601 string.
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _bump_monotonic(previous: datetime) -> datetime:
    current = _now_utc_iso()
    if current <= previous:
        # bump microseconds deterministically
        current = previous.replace()
        current = current.replace(microsecond=current.microsecond + 1)
    return current


def _dict_from_row(row: sqlite3.Row) -> dict[str, Any]:
    return {k: row[k] for k in row.keys()}


def _validate_revenue(value: Any) -> float:
    try:
        revenue = float(value)
    except (TypeError, ValueError) as e:
        raise ValueError("entity_revenue must be a number") from e
    if math.isnan(revenue) or math.isinf(revenue):
        raise ValueError("entity_revenue must be a finite number")
    return revenue


class Entity6Service:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        revenue = _validate_revenue(payload["entity_revenue"])
        now = _now_utc_iso()

        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO Entity6 (
                    entity_name,
                    entity_revenue,
                    entity_revenue_last2years,
                    entity_creation_date,
                    entity_updated_date,
                    created_by,
                    updated_by,
                    import_source,
                    external_reference,
                    notes,
                    is_deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    payload["entity_name"],
                    revenue,
                    _validate_revenue(payload["entity_revenue_last2years"]),
                    now,
                    now,
                    payload.get("created_by"),
                    payload.get("updated_by"),
                    payload.get("import_source"),
                    payload.get("external_reference"),
                    payload.get("notes"),
                ),
            )
            entity6_id = int(cur.lastrowid)
            row = conn.execute(
                "SELECT * FROM Entity6 WHERE Entity6Id = ?", (entity6_id,)
            ).fetchone()
            assert row is not None
            return self._format_row(row)

    def get_by_id(self, entity6_id: int) -> dict[str, Any]:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT * FROM Entity6 WHERE Entity6Id = ?", (entity6_id,)
            )
            row = cur.fetchone()
            if row is None:
                raise NotFoundError(entity6_id)
            return self._format_row(row)

    def update(self, entity6_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        if not payload:
            raise ValueError("No update fields provided")

        with self._connect() as conn:
            cur = conn.execute(
                "SELECT * FROM Entity6 WHERE Entity6Id = ?", (entity6_id,)
            )
            row = cur.fetchone()
            if row is None:
                raise NotFoundError(entity6_id)
            previous_updated = _parse_db_datetime(row["entity_updated_date"])
            new_updated = _bump_monotonic(previous_updated)

            set_clauses: list[str] = []
            values: list[Any] = []
            allowed = {
                "entity_name",
                "entity_revenue",
                "entity_revenue_last2years",
                "created_by",
                "updated_by",
                "import_source",
                "external_reference",
                "notes",
            }
            for k, v in payload.items():
                if k not in allowed:
                    continue
                if v is None:
                    continue
                if k in {"entity_revenue", "entity_revenue_last2years"}:
                    v = _validate_revenue(v)
                set_clauses.append(f"{k} = ?")
                values.append(v)

            set_clauses.append("entity_updated_date = ?")
            values.append(new_updated)
            values.append(entity6_id)

            sql = f"UPDATE Entity6 SET {', '.join(set_clauses)} WHERE Entity6Id = ?"
            conn.execute(sql, tuple(values))
            row = conn.execute(
                "SELECT * FROM Entity6 WHERE Entity6Id = ?", (entity6_id,)
            ).fetchone()
            assert row is not None
            return self._format_row(row)

    def delete(self, entity6_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM Entity6 WHERE Entity6Id = ?", (entity6_id,)
            )
            deleted = cur.rowcount or 0
            conn.commit()
            return deleted > 0

    def _format_row(self, row: sqlite3.Row) -> dict[str, Any]:
        d = _dict_from_row(row)
        # normalize datetime fields to datetime objects for pydantic
        d["entity_creation_date"] = _parse_db_datetime(d["entity_creation_date"])
        d["entity_updated_date"] = _parse_db_datetime(d["entity_updated_date"])
        # SQLite returns floats already for FLOAT columns
        d["entity_revenue"] = float(d["entity_revenue"])
        d["entity_revenue_last2years"] = float(d["entity_revenue_last2years"])
        d["is_deleted"] = int(d["is_deleted"])
        d["Entity6Id"] = int(d["Entity6Id"])
        return d
d_date"])
        # SQLite returns floats already for FLOAT columns
        d["entity_revenue"] = float(d["entity_revenue"])
        d["entity_revenue_last2years"] = float(d["entity_revenue_last2years"])
        d["is_deleted"] = int(d["is_deleted"])
        d["Entity6Id"] = int(d["Entity6Id"])
        return d
