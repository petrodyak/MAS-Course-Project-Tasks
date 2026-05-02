from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from typing import Optional

from .entity10_time_utils import utc_iso8601_now
from .entity10_db_schema import TABLE_NAME


@dataclass(frozen=True)
class Entity10Record:
    entity_id: str
    entity_name: str
    entity_revenue: Optional[float]
    entity_creation_date: str
    entity_updated_date: str


class Entity10Repository:
    def __init__(self, db_path: str):
        self._db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create(self, entity_name: str, entity_revenue: Optional[float]) -> Entity10Record:
        if entity_name is None:
            raise ValueError("entity_name cannot be NULL")

        entity_id = str(uuid.uuid4())
        now = utc_iso8601_now()

        with self._connect() as conn:
            cur = conn.execute(
                f"""
                INSERT INTO {TABLE_NAME} (
                    entity_id,
                    entity_name,
                    entity_revenue,
                    entity_creation_date,
                    entity_updated_date
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (entity_id, entity_name, entity_revenue, now, now),
            )
            if cur.rowcount != 1:
                # Should never happen for a single-row insert, but keep explicit.
                raise RuntimeError("Failed to insert Entity10 record")

            row = conn.execute(
                f"SELECT * FROM {TABLE_NAME} WHERE entity_id = ?", (entity_id,)
            ).fetchone()
            assert row is not None

            return Entity10Record(
                entity_id=row["entity_id"],
                entity_name=row["entity_name"],
                entity_revenue=row["entity_revenue"],
                entity_creation_date=row["entity_creation_date"],
                entity_updated_date=row["entity_updated_date"],
            )

    def get_by_id(self, entity_id: str) -> Entity10Record | None:
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT * FROM {TABLE_NAME} WHERE entity_id = ?", (entity_id,)
            ).fetchone()
            if row is None:
                return None
            return Entity10Record(
                entity_id=row["entity_id"],
                entity_name=row["entity_name"],
                entity_revenue=row["entity_revenue"],
                entity_creation_date=row["entity_creation_date"],
                entity_updated_date=row["entity_updated_date"],
            )

    def list(self, limit: int = 100, offset: int = 0) -> list[Entity10Record]:
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM {TABLE_NAME}
                ORDER BY entity_id
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()
            return [
                Entity10Record(
                    entity_id=r["entity_id"],
                    entity_name=r["entity_name"],
                    entity_revenue=r["entity_revenue"],
                    entity_creation_date=r["entity_creation_date"],
                    entity_updated_date=r["entity_updated_date"],
                )
                for r in rows
            ]

    def update(
        self,
        entity_id: str,
        *,
        entity_name: str,
        entity_revenue: Optional[float],
    ) -> Entity10Record | None:
        if entity_name is None:
            raise ValueError("entity_name cannot be NULL")

        now = utc_iso8601_now()

        with self._connect() as conn:
            existing = conn.execute(
                f"SELECT entity_creation_date FROM {TABLE_NAME} WHERE entity_id = ?",
                (entity_id,),
            ).fetchone()
            if existing is None:
                return None

            conn.execute(
                f"""
                UPDATE {TABLE_NAME}
                SET entity_name = ?,
                    entity_revenue = ?,
                    entity_updated_date = ?
                WHERE entity_id = ?
                """,
                (entity_name, entity_revenue, now, entity_id),
            )

            row = conn.execute(
                f"SELECT * FROM {TABLE_NAME} WHERE entity_id = ?", (entity_id,)
            ).fetchone()
            assert row is not None

            return Entity10Record(
                entity_id=row["entity_id"],
                entity_name=row["entity_name"],
                entity_revenue=row["entity_revenue"],
                entity_creation_date=row["entity_creation_date"],
                entity_updated_date=row["entity_updated_date"],
            )

    def delete(self, entity_id: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                f"DELETE FROM {TABLE_NAME} WHERE entity_id = ?", (entity_id,)
            )
            return cur.rowcount == 1
