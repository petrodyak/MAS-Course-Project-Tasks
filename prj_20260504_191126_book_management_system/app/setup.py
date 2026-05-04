from __future__ import annotations

import os
import sqlite3


def ensure_setup(db_path: str, artifacts_path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    os.makedirs(artifacts_path, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys=ON")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rooms (
                room_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                room_name VARCHAR(255) NOT NULL,
                location VARCHAR(255) NOT NULL,
                room_capacity INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS shelves (
                shelf_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                shelf_name VARCHAR(255) NOT NULL,
                room_id INTEGER NOT NULL,
                shelf_capacity INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(room_id) REFERENCES rooms(room_id) ON DELETE RESTRICT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                book_title VARCHAR(500) NOT NULL,
                isbn VARCHAR(32) NOT NULL,
                author VARCHAR(255) NOT NULL,
                shelf_id INTEGER NOT NULL,
                published_date DATETIME NULL,
                book_description TEXT NULL,
                is_available BOOLEAN NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(shelf_id) REFERENCES shelves(shelf_id) ON DELETE NO ACTION
            )
            """
        )

        conn.execute("CREATE INDEX IF NOT EXISTS idx_shelves_room_id ON shelves(room_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_books_shelf_id ON books(shelf_id)")
        conn.commit()
