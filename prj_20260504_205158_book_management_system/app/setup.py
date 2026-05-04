from __future__ import annotations
import os
import sqlite3


def ensure_setup(db_path: str, artifacts_path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    os.makedirs(artifacts_path, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rooms (
                room_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                room_name TEXT NOT NULL,
                room_description TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS shelves (
                shelf_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                shelf_name TEXT NOT NULL,
                shelf_code TEXT NOT NULL,
                shelf_description TEXT NOT NULL,
                room_id INTEGER NOT NULL REFERENCES rooms(room_id),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                book_title TEXT NOT NULL,
                book_author TEXT NOT NULL,
                book_isbn TEXT NOT NULL,
                book_genre TEXT NOT NULL,
                book_publication_year INTEGER NOT NULL,
                book_language TEXT NOT NULL,
                book_status TEXT NOT NULL,
                shelf_id INTEGER NOT NULL REFERENCES shelves(shelf_id),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.commit()
