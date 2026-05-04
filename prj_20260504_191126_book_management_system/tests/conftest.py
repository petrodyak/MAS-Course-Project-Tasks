from __future__ import annotations

import os
import sqlite3
import pytest


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "data" / "app.db")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


@pytest.fixture
def conn(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.commit()
    yield conn
    conn.close()
