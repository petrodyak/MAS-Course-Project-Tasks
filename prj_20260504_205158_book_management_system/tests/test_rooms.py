from __future__ import annotations
from tests.conftest import AUTH


def test_list_rooms_empty(client):
    r = client.get("/rooms", headers=AUTH)
    assert r.status_code == 200
    assert r.json() == []


def test_create_room(client):
    r = client.post(
        "/rooms",
        json={"room_name": "A1", "room_description": "First room"},
        headers=AUTH,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["room_name"] == "A1"
    assert "room_id" in data


def test_get_room(client):
    r = client.post(
        "/rooms",
        json={"room_name": "R1", "room_description": "desc"},
        headers=AUTH,
    )
    room_id = r.json()["room_id"]

    r2 = client.get(f"/rooms/{room_id}", headers=AUTH)
    assert r2.status_code == 200
    assert r2.json()["room_id"] == room_id


def test_get_room_not_found(client):
    r = client.get("/rooms/9999", headers=AUTH)
    assert r.status_code == 404


def test_update_room(client):
    r = client.post(
        "/rooms",
        json={"room_name": "Old", "room_description": "old desc"},
        headers=AUTH,
    )
    room_id = r.json()["room_id"]

    r2 = client.put(
        f"/rooms/{room_id}",
        json={"room_name": "New", "room_description": "new desc"},
        headers=AUTH,
    )
    assert r2.status_code == 200
    assert r2.json()["room_name"] == "New"


def test_delete_room_no_shelves(client):
    r = client.post(
        "/rooms",
        json={"room_name": "ToDelete", "room_description": "d"},
        headers=AUTH,
    )
    room_id = r.json()["room_id"]

    r2 = client.delete(f"/rooms/{room_id}", headers=AUTH)
    assert r2.status_code == 204

    r3 = client.get(f"/rooms/{room_id}", headers=AUTH)
    assert r3.status_code == 404


def test_delete_room_with_shelves_rejected(client):
    room = client.post(
        "/rooms",
        json={"room_name": "R1", "room_description": "d"},
        headers=AUTH,
    ).json()
    client.post(
        "/shelves",
        json={
            "shelf_name": "S1",
            "shelf_code": "SC1",
            "shelf_description": "d",
            "room_id": room["room_id"],
        },
        headers=AUTH,
    )

    r = client.delete(f"/rooms/{room['room_id']}", headers=AUTH)
    assert r.status_code == 400
    assert "shelves" in r.json()["detail"].lower()


def test_list_shelves_in_room_returns_only_that_room(client):
    r1 = client.post(
        "/rooms", json={"room_name": "R1", "room_description": "d"}, headers=AUTH
    ).json()
    r2 = client.post(
        "/rooms", json={"room_name": "R2", "room_description": "d"}, headers=AUTH
    ).json()

    client.post(
        "/shelves",
        json={
            "shelf_name": "S1",
            "shelf_code": "SC1",
            "shelf_description": "d",
            "room_id": r1["room_id"],
        },
        headers=AUTH,
    )
    client.post(
        "/shelves",
        json={
            "shelf_name": "S2",
            "shelf_code": "SC2",
            "shelf_description": "d",
            "room_id": r2["room_id"],
        },
        headers=AUTH,
    )

    resp = client.get(f"/rooms/{r1['room_id']}/shelves", headers=AUTH)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["shelf_name"] == "S1"


def test_unauthorized_without_token(client):
    r = client.get("/rooms")
    assert r.status_code == 401
