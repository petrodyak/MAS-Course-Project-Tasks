from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class DistrictRow:
    district_id: int
    city_id: int
    name: str
    code: str | None
    type: str
    status: str


class DistrictRepository:
    def __init__(self, db_path: str):
        self._db_path = db_path

    def create(
        self,
        *,
        city_id: int,
        name: str,
        code: str | None,
        type: str,
        status: str,
    ) -> int:
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.execute(
                """
                INSERT INTO district (city_id, name, code, type, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (city_id, name, code, type, status),
            )
            district_id = int(cur.lastrowid)
            return district_id

    def get(self, district_id: int) -> DistrictRow | None:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT district_id, city_id, name, code, type, status FROM district WHERE district_id = ?",
                (district_id,),
            ).fetchone()
            if row is None:
                return None
            return DistrictRow(
                district_id=int(row["district_id"]),
                city_id=int(row["city_id"]),
                name=str(row["name"]),
                code=row["code"],
                type=str(row["type"]),
                status=str(row["status"]),
            )

    def update(
        self,
        district_id: int,
        *,
        city_id: int | None = None,
        name: str | None = None,
        code: str | None = None,
        type: str | None = None,
        status: str | None = None,
    ) -> None:
        fields: list[tuple[str, object | None]] = []
        if city_id is not None:
            fields.append(("city_id", city_id))
        if name is not None:
            fields.append(("name", name))
        if code is not None:
            fields.append(("code", code))
        if type is not None:
            fields.append(("type", type))
        if status is not None:
            fields.append(("status", status))

        if not fields:
            return

        set_clause = ", ".join([f"{k} = ?" for k, _ in fields])
        params = [v for _, v in fields] + [district_id]
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                f"UPDATE district SET {set_clause} WHERE district_id = ?",
                params,
            )

    def delete(self, district_id: int) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("DELETE FROM district WHERE district_id = ?", (district_id,))

    def list(
        self,
        *,
        city_id: int | None = None,
        status: str | None = None,
        type: str | None = None,
    ) -> list[DistrictRow]:
        where: list[str] = []
        params: list[object] = []
        if city_id is not None:
            where.append("city_id = ?")
            params.append(city_id)
        if status is not None:
            where.append("status = ?")
            params.append(status)
        if type is not None:
            where.append("type = ?")
            params.append(type)

        sql = (
            "SELECT district_id, city_id, name, code, type, status FROM district"
        )
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY district_id ASC"

        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, params).fetchall()
            return [
                DistrictRow(
                    district_id=int(r["district_id"]),
                    city_id=int(r["city_id"]),
                    name=str(r["name"]),
                    code=r["code"],
                    type=str(r["type"]),
                    status=str(r["status"]),
                )
                for r in rows
            ]
