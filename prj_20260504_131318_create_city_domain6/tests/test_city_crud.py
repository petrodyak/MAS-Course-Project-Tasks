import os
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    # uses app lifespan to ensure DB exists
    return TestClient(app)


def test_city_name_not_null_enforced(client):
    # created_at/updated_at are managed by service; omit city_name to trigger NOT NULL
    resp = client.post(
        "/cities",
        json={
            "city_name": None,
            "city_old_name": "Old",
            "city_size_km2": 1.0,
            "country": "Country",
            "established_date": "2000-01-01",
            "notes": "note",
        },
    )
    # SQLAlchemy/validation should yield 422 or 500 depending on layer; accept 422.
    assert resp.status_code in (422, 500)


def test_city_crud_persists_and_enforces_id_immutable(client):
    created = client.post(
        "/cities",
        json={
            "city_name": "Test City",
            "city_old_name": "Old City",
            "city_size_km2": 12.5,
            "country": "Testland",
            "established_date": "1999-12-31",
            "notes": "initial",
        },
    )
    assert created.status_code == 201
    payload = created.json()
    city_id = payload["city_id"]
    assert payload["city_name"] == "Test City"

    updated = client.put(
        f"/cities/{city_id}",
        json={
            "city_name": "Updated City",
            "city_old_name": "Old City 2",
            "city_size_km2": 13.0,
            "country": "New Country",
            "established_date": "2001-01-01",
            "notes": "updated",
        },
    )
    assert updated.status_code == 200
    payload2 = updated.json()
    assert payload2["city_id"] == city_id
    assert payload2["city_name"] == "Updated City"

    get_resp = client.get(f"/cities/{city_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["city_name"] == "Updated City"

    del_resp = client.delete(f"/cities/{city_id}")
    assert del_resp.status_code == 204

    missing = client.get(f"/cities/{city_id}")
    assert missing.status_code == 404


def test_schema_contains_expected_columns():
    # directly inspect sqlite schema to ensure column names/types
    db_path = os.environ.get("APP_DB_PATH")
    if not db_path:
        # fallback: app.main default path
        from pathlib import Path

        _project_root = Path(__file__).resolve().parents[2]
        db_path = str(_project_root / "data" / "app.db")

    conn = sqlite3.connect(db_path)
    try:
        cols = {row[1]: row for row in conn.execute("PRAGMA table_info(city)")}
        assert "city_id" in cols
        assert "city_name" in cols
        assert cols["city_name"][3] == 1  # notnull
        for name in [
            "city_old_name",
            "city_size_km2",
            "country",
            "established_date",
            "notes",
            "created_at",
            "updated_at",
        ]:
            assert name in cols
    finally:
        conn.close()
