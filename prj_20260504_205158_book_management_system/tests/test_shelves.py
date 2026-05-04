from __future__ import annotations
import pytest
from tests.conftest import AUTH


@pytest.fixture
def room(client):
    r = client.post(
        "/rooms",
        json={"room_name": "TestRoom", "room_description": "d"},
        headers=AUTH,
    )
    return r.json()


def _shelf_payload(room_id: int, name: str = "S1", code: str = "SC1") -> dict:
    return {
        "shelf_name": name,
        "shelf_code": code,
        "shelf_description": "test shelf",
        "room_id": room_id,
    }


def test_create_shelf_valid_room(client, room):
    r = client.post("/shelves", json=_shelf_payload(room["room_id"]), headers=AUTH)
    assert r.status_code == 201
    assert r.json()["room_id"] == room["room_id"]
    assert r.json()["shelf_name"] == "S1"


def test_create_shelf_invalid_room_rejected(client):
    r = client.post("/shelves", json=_shelf_payload(9999), headers=AUTH)
    assert r.status_code == 400
    assert "room" in r.json()["detail"].lower()


def test_update_shelf_invalid_room_rejected(client, room):
    shelf = client.post(
        "/shelves", json=_shelf_payload(room["room_id"]), headers=AUTH
    ).json()

    r = client.put(
        f"/shelves/{shelf['shelf_id']}",
        json=_shelf_payload(9999),
        headers=AUTH,
    )
    assert r.status_code == 400


def test_update_shelf_success(client, room):
    shelf = client.post(
        "/shelves", json=_shelf_payload(room["room_id"]), headers=AUTH
    ).json()

    r = client.put(
        f"/shelves/{shelf['shelf_id']}",
        json={**_shelf_payload(room["room_id"]), "shelf_name": "Updated"},
        headers=AUTH,
    )
    assert r.status_code == 200
    assert r.json()["shelf_name"] == "Updated"
    assert r.json()["room_id"] == room["room_id"]


def test_delete_shelf_no_books(client, room):
    shelf = client.post(
        "/shelves", json=_shelf_payload(room["room_id"]), headers=AUTH
    ).json()

    r = client.delete(f"/shelves/{shelf['shelf_id']}", headers=AUTH)
    assert r.status_code == 204


def test_delete_shelf_with_books_rejected(client, room):
    shelf = client.post(
        "/shelves", json=_shelf_payload(room["room_id"]), headers=AUTH
    ).json()
    client.post(
        "/books",
        json={
            "shelf_id": shelf["shelf_id"],
            "book_title": "T",
            "book_author": "A",
            "book_isbn": "123",
            "book_genre": "F",
            "book_publication_year": 2000,
            "book_language": "EN",
            "book_status": "available",
        },
        headers=AUTH,
    )

    r = client.delete(f"/shelves/{shelf['shelf_id']}", headers=AUTH)
    assert r.status_code == 400
    assert "books" in r.json()["detail"].lower()


def test_list_books_on_shelf_filtered(client, room):
    s1 = client.post(
        "/shelves", json=_shelf_payload(room["room_id"], "S1", "SC1"), headers=AUTH
    ).json()
    s2 = client.post(
        "/shelves", json=_shelf_payload(room["room_id"], "S2", "SC2"), headers=AUTH
    ).json()

    client.post(
        "/books",
        json={
            "shelf_id": s1["shelf_id"],
            "book_title": "BookOnS1",
            "book_author": "A",
            "book_isbn": "111",
            "book_genre": "F",
            "book_publication_year": 2000,
            "book_language": "EN",
            "book_status": "available",
        },
        headers=AUTH,
    )
    client.post(
        "/books",
        json={
            "shelf_id": s2["shelf_id"],
            "book_title": "BookOnS2",
            "book_author": "A",
            "book_isbn": "222",
            "book_genre": "F",
            "book_publication_year": 2001,
            "book_language": "EN",
            "book_status": "available",
        },
        headers=AUTH,
    )

    r = client.get(f"/shelves/{s1['shelf_id']}/books", headers=AUTH)
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 1
    assert items[0]["book_title"] == "BookOnS1"
