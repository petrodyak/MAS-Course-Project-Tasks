from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.setup import ensure_setup
from app.repositories.entity9_repository import Entity9NotFoundError
from app.services.entity9_service import Entity9Service


@pytest.fixture()
def db_file(tmp_path: Path) -> str:
    db_path = str(tmp_path / "app.db")
    artifacts_path = str(tmp_path / "artifacts")
    ensure_setup(db_path, artifacts_path)
    return db_path


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def test_schema_column_names(db_file: str):
    conn = _connect(db_file)
    try:
        cursor = conn.execute("PRAGMA table_info(entity9)")
        columns = {row["name"] for row in cursor.fetchall()}
        assert {"id", "entity_name", "entity_revenue", "entity_creation_date", "entity_updated_date"}.issubset(columns)
    finally:
        conn.close()


def test_schema_column_types(db_file: str):
    conn = _connect(db_file)
    try:
        cursor = conn.execute("PRAGMA table_info(entity9)")
        types = {row["name"]: str(row["type"]).upper() for row in cursor.fetchall()}
        assert types["id"] == "TEXT" or "CHAR" in types["id"]
        assert types["entity_name"] == "TEXT"
        assert types["entity_revenue"] == "REAL"
        # SQLite stores TEXT affinity, but keep loose asserts.
        assert types["entity_creation_date"].startswith("TEXT")
        assert types["entity_updated_date"].startswith("TEXT")
    finally:
        conn.close()


def test_entity_revenue_allows_null_and_negative(db_file: str):
    service = Entity9Service(db_file)
    service.create_entity9(id="e1", entity_name="Acme", entity_revenue=None)
    service.create_entity9(id="e2", entity_name="Beta", entity_revenue=-123.45)

    conn = _connect(db_file)
    try:
        row1 = conn.execute("SELECT entity_revenue FROM entity9 WHERE id = ?", ("e1",)).fetchone()
        row2 = conn.execute("SELECT entity_revenue FROM entity9 WHERE id = ?", ("e2",)).fetchone()
        assert row1[0] is None
        assert float(row2[0]) == -123.45
    finally:
        conn.close()


def test_entity_name_not_null_constraint(db_file: str):
    service = Entity9Service(db_file)
    with pytest.raises(sqlite3.IntegrityError):
        service.create_entity9(id="e3", entity_name=None, entity_revenue=1.0)  # type: ignore[arg-type]


def test_update_delete(db_file: str):
    service = Entity9Service(db_file)
    service.create_entity9(id="e4", entity_name="Gamma", entity_revenue=1.0)
    updated = service.update_entity9(id="e4", entity_name="Gamma2", entity_revenue=None)
    assert updated.entity_name == "Gamma2"
    assert updated.entity_revenue is None

    service.delete_entity9(id="e4")
    with pytest.raises(Entity9NotFoundError):
        service.delete_entity9(id="e4")


def test_migration_idempotent(tmp_path: Path):
    db = str(tmp_path / "test.db")
    artifacts = str(tmp_path / "artifacts")

    ensure_setup(db, artifacts)
    ensure_setup(db, artifacts)

    conn = sqlite3.connect(db)
    try:
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        ]
        assert "entity9" in tables
    finally:
        conn.close()
