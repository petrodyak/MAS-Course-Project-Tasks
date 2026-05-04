from __future__ import annotations

import sqlite3

import pytest

from app.setup import ensure_setup


def test_fk_delete_restrict_behavior(conn, db_path):
    import os
    artifacts = os.path.join(os.path.dirname(db_path), "artifacts")
    ensure_setup(db_path, artifacts)
    # rooms ON DELETE RESTRICT for dependent shelves
    cur = conn.execute(
        "INSERT INTO rooms (room_name, location, room_capacity) VALUES (?, ?, ?)",
        ("Room A", "Loc", 10),
    )
    room_id = cur.lastrowid

    cur = conn.execute(
        "INSERT INTO shelves (shelf_name, room_id, shelf_capacity) VALUES (?, ?, ?)",
        ("Shelf 1", room_id, 100),
    )
    shelf_id = cur.lastrowid

    conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM rooms WHERE room_id = ?", (room_id,))
        conn.commit()

    # shelves ON DELETE RESTRICT for dependent books
    cur = conn.execute(
        "INSERT INTO books (book_title, isbn, author, shelf_id, is_available) VALUES (?, ?, ?, ?, ?)",
        ("Book 1", "ISBN-1", "Author", shelf_id, 1),
    )
    book_id = cur.lastrowid
    conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM shelves WHERE shelf_id = ?", (shelf_id,))
        conn.commit()
