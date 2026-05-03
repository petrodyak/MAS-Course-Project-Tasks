from __future__ import annotations

import sqlite3
import pytest


@pytest.fixture()
def conn(tmp_path):
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    yield conn
    conn.close()
