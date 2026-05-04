from __future__ import annotations

import os
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = str(tmp_path / "data" / "app.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    monkeypatch.setenv("BOOK_DB_PATH", db_path)
    monkeypatch.setenv("BOOK_ARTIFACTS_PATH", str(tmp_path / "artifacts"))

    with TestClient(app) as c:
        yield c


def test_create_room_shelf_book_and_get_location(client):
    r = client.post(
        "/rooms",
        json={"room_name": "Room A", "location": "Floor 1", "room_capacity": 10},
    )
    assert r.status_code == 201
    room_id = r.json()["room_id"]

    s = client.post(
        "/shelves",
        json={"shelf_name": "Shelf 1", "room_id": room_id, "shelf_capacity": 100},
    )
    assert s.status_code == 201
    shelf_id = s.json()["shelf_id"]

    b = client.post(
        "/books",
        json={
            "book_title": "Book 1",
            "isbn": "1234567890",
            "author": "Author 1",
            "shelf_id": shelf_id,
            "is_available": True,
            "book_description": "desc",
        },
    )
    assert b.status_code == 201
    book_id = b.json()["book_id"]

    loc = client.get(f"/books/{book_id}/location")
    assert loc.status_code == 200
    data = loc.json()
    assert data["book_id"] == book_id
    assert data["room_id"] == room_id
    assert data["shelf_id"] == shelf_id
    assert data["room_name"] == "Room A"
    assert data["shelf_name"] == "Shelf 1"


def test_foreign_key_rejects_nonexistent_room(client):
    s = client.post(
        "/shelves",
        json={"shelf_name": "Shelf X", "room_id": 9999, "shelf_capacity": 1},
    )
    assert s.status_code == 404


def test_foreign_key_rejects_nonexistent_shelf(client):
    b = client.post(
        "/books",
        json={
            "book_title": "Book X",
            "isbn": "111",
            "author": "A",
            "shelf_id": 8888,
            "is_available": False,
        },
    )
    assert b.status_code == 404


def test_not_null_book_fields(client):
    b = client.post(
        "/books",
        json={
            "isbn": "111",
            "author": "A",
            "shelf_id": 1,
            "is_available": False,
        },
    )
    assert b.status_code == 422
