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
