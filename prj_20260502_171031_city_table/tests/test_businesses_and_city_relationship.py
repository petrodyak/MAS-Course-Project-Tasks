from __future__ import annotations

import sqlite3

import pytest

from app.business_repository_sqlite import BusinessRepositorySQLite
from app.business_service import BusinessService
from app.business_type import BusinessType
from app.setup import ensure_setup


def test_business_crud_scoped_to_city(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    ensure_setup(db_path, str(tmp_path / "art"))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        c1 = conn.execute("INSERT INTO city (city_name) VALUES (?)", ("Kyiv",))
        city1_id = c1.lastrowid
        c2 = conn.execute("INSERT INTO city (city_name) VALUES (?)", ("Lviv",))
        city2_id = c2.lastrowid
        conn.commit()  # release write lock before the service opens its own connection

        service = BusinessService(BusinessRepositorySQLite(db_path))

        service.create_business(
            name="Acme Inc",
            type=BusinessType.COMPANY.value,
            city_id=city1_id,
            description=None,
            established_year=None,
        )
        service.create_business(
            name="Green Store",
            type=BusinessType.STORE_SHOP.value,
            city_id=city1_id,
        )
        service.create_business(
            name="Sky Diner",
            type=BusinessType.RESTAURANT.value,
            city_id=city2_id,
        )

        b1 = service.list_businesses_for_city(city1_id)
        assert [b["city_id"] for b in b1] == [city1_id, city1_id]
        assert {b["type"] for b in b1} == {
            BusinessType.COMPANY.value,
            BusinessType.STORE_SHOP.value,
        }

        b2 = service.list_businesses_for_city(city2_id)
        assert len(b2) == 1
        assert b2[0]["city_id"] == city2_id

        b_empty = service.list_businesses_for_city(999999)
        assert b_empty == []
    finally:
        conn.close()


def test_business_type_validation_rejects_invalid_value(tmp_path):
    db_path = str(tmp_path / "db.sqlite")
    ensure_setup(db_path, str(tmp_path / "art"))

    conn = sqlite3.connect(db_path)
    try:
        city_id = conn.execute("INSERT INTO city (city_name) VALUES (?)", ("Kyiv",)).lastrowid
    finally:
        conn.close()

    service = BusinessService(BusinessRepositorySQLite(db_path))

    with pytest.raises(ValueError):
        service.create_business(
            name="Hotel X",
            type="Hotel",
            city_id=city_id,
        )
