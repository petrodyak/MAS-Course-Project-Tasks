from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class City:
    id: int
    city_name: str
    city_size_sq_km: float | None = None
    country: str | None = None
    establishment_date: str | None = None
    notes: str | None = None


class CityRepository:
    def __init__(self, db_path: str):
        self._db_path = db_path

    def create(
        self,
        city_name: str,
        city_size_sq_km: float | None = None,
        country: str | None = None,
        establishment_date: str | None = None,
        notes: str | None = None,
    ) -> int:
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.execute(
                """
                INSERT INTO city
                    (city_name, city_size_sq_km, country, establishment_date, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                (city_name, city_size_sq_km, country, establishment_date, notes),
            )
            return int(cur.lastrowid)

    def get(self, city_id: int) -> City | None:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM city WHERE id = ?", (city_id,)).fetchone()
            if row is None:
                return None
            return City(
                id=int(row["id"]),
                city_name=str(row["city_name"]),
                city_size_sq_km=row["city_size_sq_km"],
                country=row["country"],
                establishment_date=row["establishment_date"],
                notes=row["notes"],
            )

    def update(
        self,
        city_id: int,
        *,
        city_name: str | None = None,
        city_size_sq_km: float | None = None,
        country: str | None = None,
        establishment_date: str | None = None,
        notes: str | None = None,
    ) -> None:
        fields: list[tuple[str, Any]] = []
        if city_name is not None:
            fields.append(("city_name", city_name))
        if city_size_sq_km is not None:
            fields.append(("city_size_sq_km", city_size_sq_km))
        if country is not None:
            fields.append(("country", country))
        if establishment_date is not None:
            fields.append(("establishment_date", establishment_date))
        if notes is not None:
            fields.append(("notes", notes))

        if not fields:
            return

        set_clause = ", ".join([f"{k} = ?" for k, _ in fields])
        params = [v for _, v in fields] + [city_id]

        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                f"UPDATE city SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                params,
            )

    def delete(self, city_id: int) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("DELETE FROM city WHERE id = ?", (city_id,))
