from __future__ import annotations

import sqlite3
from typing import Optional

from app.models.entity9 import Entity9


class Entity9NotFoundError(Exception):
    pass


class Entity9Repository:
    def __init__(self, db_path: str):
        self._db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        # Foreign keys are not required here, but keep default explicit.
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def create(
        self,
        *,
        id: str,
        entity_name: str,
        entity_revenue: Optional[float],
        entity_creation_date: str,
        entity_updated_date: str,
    ) -> Entity9:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO entity9 (
                    id, entity_name, entity_revenue,
                    entity_creation_date, entity_updated_date
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    id,
                    entity_name,
                    entity_revenue,
                    entity_creation_date,
                    entity_updated_date,
                ),
            )
            _ = cur.rowcount
            row = conn.execute("SELECT * FROM entity9 WHERE id = ?", (id,)).fetchone()
            assert row is not None
            return self._from_row(row)

    def get_by_id(self, id: str) -> Entity9:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM entity9 WHERE id = ?", (id,)).fetchone()
            if row is None:
                raise Entity9NotFoundError(f"Entity9 not found: {id}")
            return self._from_row(row)

    def list(self, *, limit: int = 100, offset: int = 0) -> list[Entity9]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM entity9
                ORDER BY rowid
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()
            return [self._from_row(r) for r in rows]

    def update(
        self,
        *,
        id: str,
        entity_name: str,
        entity_revenue: Optional[float],
    ) -> Entity9:
        # entity_updated_date is handled by trigger if defined, but we still
        # include it in the UPDATE statement to make behavior explicit.
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE entity9
                SET entity_name = ?,
                    entity_revenue = ?
                WHERE id = ?
                """,
                (entity_name, entity_revenue, id),
            )
            if cur.rowcount == 0:
                raise Entity9NotFoundError(f"Entity9 not found: {id}")
            row = conn.execute("SELECT * FROM entity9 WHERE id = ?", (id,)).fetchone()
            assert row is not None
            return self._from_row(row)

    def delete(self, *, id: str) -> None:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM entity9 WHERE id = ?", (id,))
            if cur.rowcount == 0:
                raise Entity9NotFoundError(f"Entity9 not found: {id}")

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Entity9:
        return Entity9(
            id=str(row["id"]),
            entity_name=str(row["entity_name"]),
            entity_revenue=row["entity_revenue"],
            entity_creation_date=str(row["entity_creation_date"]),
            entity_updated_date=str(row["entity_updated_date"]),
        )
