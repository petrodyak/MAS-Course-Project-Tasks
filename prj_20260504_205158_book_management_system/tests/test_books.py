from __future__ import annotations
import pytest
from tests.conftest import AUTH


@pytest.fixture
def shelf(client):
    room = client.post(
        "/rooms",
        json={"room_name": "R1", "room_description": "d"},
        headers=AUTH,
    ).json()
    s = client.post(
        "/shelves",
        json={
            "shelf_name": "S1",
            "shelf_code": "SC1",
            "shelf_description": "d",
            "room_id": room["room_id"],
        },
        headers=AUTH,
    ).json()
    return {"shelf": s, "room": room}


def _book(shelf_id: int, title: str = "My Book") -> dict:
    return {
        "shelf_id": shelf_id,
        "book_title": title,
        "book_author": "Author",
        "book_isbn": "978-0000000000",
        "book_genre": "Fiction",
        "book_publication_year": 2020,
        "book_language": "English",
        "book_status": "available",
    }


def test_create_book_valid_shelf(client, shelf):
    r = client.post("/books", json=_book(shelf["shelf"]["shelf_id"]), headers=AUTH)
    assert r.status_code == 201
    assert r.json()["book_title"] == "My Book"
    assert r.json()["shelf_id"] == shelf["shelf"]["shelf_id"]


def test_create_book_invalid_shelf_rejected(client):
    r = client.post("/books", json=_book(9999), headers=AUTH)
    assert r.status_code == 400
    assert "shelf" in r.json()["detail"].lower()


def test_get_book_includes_room_id(client, shelf):
    book = client.post(
        "/books", json=_book(shelf["shelf"]["shelf_id"]), headers=AUTH
    ).json()

    r = client.get(f"/books/{book['book_id']}", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "room_id" in data
    assert data["room_id"] == shelf["room"]["room_id"]


def test_delete_book_only_removes_that_book(client, shelf):
    shelf_id = shelf["shelf"]["shelf_id"]
    b1 = client.post("/books", json=_book(shelf_id, "Book 1"), headers=AUTH).json()
    b2 = client.post("/books", json=_book(shelf_id, "Book 2"), headers=AUTH).json()

    r = client.delete(f"/books/{b1['book_id']}", headers=AUTH)
    assert r.status_code == 204

    assert client.get(f"/books/{b2['book_id']}", headers=AUTH).status_code == 200
    assert client.get(f"/books/{b1['book_id']}", headers=AUTH).status_code == 404
    assert client.get(f"/shelves/{shelf_id}", headers=AUTH).status_code == 200


def test_update_book_preserves_shelf_when_unchanged(client, shelf):
    shelf_id = shelf["shelf"]["shelf_id"]
    book = client.post("/books", json=_book(shelf_id), headers=AUTH).json()

    r = client.put(
        f"/books/{book['book_id']}",
        json={**_book(shelf_id), "book_title": "Updated", "book_status": "checked_out"},
        headers=AUTH,
    )
    assert r.status_code == 200
    assert r.json()["book_title"] == "Updated"
    assert r.json()["shelf_id"] == shelf_id


def test_reassign_book_to_different_shelf(client, shelf):
    room_id = shelf["room"]["room_id"]
    shelf_id = shelf["shelf"]["shelf_id"]

    s2 = client.post(
        "/shelves",
        json={
            "shelf_name": "S2", "shelf_code": "SC2",
            "shelf_description": "d", "room_id": room_id,
        },
        headers=AUTH,
    ).json()

    book = client.post("/books", json=_book(shelf_id, "Traveler"), headers=AUTH).json()
    book_id = book["book_id"]

    r = client.put(
        f"/books/{book_id}",
        json={**_book(s2["shelf_id"], "Traveler")},
        headers=AUTH,
    )
    assert r.status_code == 200
    assert r.json()["shelf_id"] == s2["shelf_id"]

    on_s2 = client.get(f"/shelves/{s2['shelf_id']}/books", headers=AUTH).json()["items"]
    assert any(b["book_id"] == book_id for b in on_s2)

    on_s1 = client.get(f"/shelves/{shelf_id}/books", headers=AUTH).json()["items"]
    assert not any(b["book_id"] == book_id for b in on_s1)


def test_update_book_invalid_shelf_rejected(client, shelf):
    book = client.post(
        "/books", json=_book(shelf["shelf"]["shelf_id"]), headers=AUTH
    ).json()

    r = client.put(
        f"/books/{book['book_id']}",
        json={**_book(9999)},
        headers=AUTH,
    )
    assert r.status_code == 400
