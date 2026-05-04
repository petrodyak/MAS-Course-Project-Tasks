from __future__ import annotations

import sqlite3

from fastapi.testclient import TestClient

from app.main import app
from app.setup import ensure_setup


def test_create_and_location_and_fk_constraints(tmp_path):
    db_path = str(tmp_path / "data" / "app.db")
    artifacts = str(tmp_path / "artifacts")
    ensure_setup(db_path, artifacts)

    app.state.db_path = db_path
    client = TestClient(app)

    room_resp = client.post(
        "/rooms",
        json={"room_name": "Room A", "location": "NY", "room_capacity": 10},
    )
    assert room_resp.status_code == 201
    room_id = room_resp.json()["room_id"]

    shelf_resp = client.post(
        "/shelves",
        json={"shelf_name": "Shelf 1", "room_id": room_id, "shelf_capacity": 5},
    )
    assert shelf_resp.status_code == 201
    shelf_id = shelf_resp.json()["shelf_id"]

    book_resp = client.post(
        "/books",
        json={
            "book_title": "Book 1",
            "isbn": "ISBN123",
            "author": "Author 1",
            "shelf_id": shelf_id,
            "published_date": None,
            "book_description": None,
            "is_available": True,
        },
    )
    assert book_resp.status_code == 201
    book_id = book_resp.json()["book_id"]

    loc_resp = client.get(f"/books/{book_id}/location")
    assert loc_resp.status_code == 200
    data = loc_resp.json()
    assert data["book_id"] == book_id
    assert data["shelf_id"] == shelf_id
    assert data["room_id"] == room_id
    assert data["room_name"] == "Room A"
    assert data["shelf_name"] == "Shelf 1"

    # FK constraint: shelf with non-existent room
    bad_shelf = client.post(
        "/shelves",
        json={
            "shelf_name": "Bad",
            "room_id": 9999,
            "shelf_capacity": 1,
        },
    )
    assert bad_shelf.status_code in {400, 404, 409, 422}


def test_delete_room_prevent_when_dependencies(tmp_path):
    db_path = str(tmp_path / "data" / "app.db")
    artifacts = str(tmp_path / "artifacts")
    ensure_setup(db_path, artifacts)

    app.state.db_path = db_path
    client = TestClient(app)

    room = client.post(
        "/rooms",
        json={"room_name": "R", "location": "L", "room_capacity": 1},
    ).json()
    room_id = room["room_id"]

    shelf = client.post(
        "/shelves",
        json={"shelf_name": "S", "room_id": room_id, "shelf_capacity": 1},
    ).json()
    shelf_id = shelf["shelf_id"]

    book = client.post(
        "/books",
        json={
            "book_title": "T",
            "isbn": "I",
            "author": "A",
            "shelf_id": shelf_id,
            "published_date": None,
            "book_description": None,
            "is_available": True,
        },
    ).json()
    assert book["book_id"]

    delete_room = client.delete(f"/rooms/{room_id}")
    # must fail due to FK constraint or HTTP 409 from service
    assert delete_room.status_code in {400, 409}
