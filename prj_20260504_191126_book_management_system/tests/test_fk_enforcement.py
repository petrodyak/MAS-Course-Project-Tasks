from __future__ import annotations

import os
import sqlite3

import pytest

from app.setup import ensure_setup


def test_fk_prevents_nonexistent_references(conn, db_path):
    artifacts = os.path.join(os.path.dirname(db_path), "artifacts")
    ensure_setup(db_path, artifacts)

    # Shelf must reference existing room
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO shelves (shelf_name, room_id, shelf_capacity) VALUES (?, ?, ?)",
            ("Invalid Shelf", 999999, 10),
        )
        conn.commit()

    # Book must reference existing shelf
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO books (book_title, isbn, author, shelf_id, is_available) VALUES (?, ?, ?, ?, ?)",
            ("Invalid Book", "ISBN-2", "Author", 999999, 1),
        )
        conn.commit()
