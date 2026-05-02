from __future__ import annotations

import sqlite3

import pytest

from app.entity10_repository import Entity10Repository
from app.setup import ensure_setup


@pytest.fixture()
def db_and_repo(tmp_path):
    db_path = str(tmp_path / "app.db")
    artifacts_path = str(tmp_path / "artifacts")
    ensure_setup(db_path, artifacts_path)
    repo = Entity10Repository(db_path=db_path)
    return db_path, repo


def test_crud_create_update_delete(db_and_repo):
    _, repo = db_and_repo

    created = repo.create(entity_name="Name1", entity_revenue=-1.25)
    assert created.entity_name == "Name1"
    assert created.entity_revenue == -1.25

    updated = repo.update(
        created.entity_id,
        entity_name="Name2",
        entity_revenue=None,
    )
    assert updated is not None
    assert updated.entity_id == created.entity_id
    assert updated.entity_name == "Name2"
    assert updated.entity_revenue is None
    assert updated.entity_updated_date != created.entity_updated_date
    assert updated.entity_creation_date == created.entity_creation_date

    assert repo.delete(created.entity_id) is True
    assert repo.get_by_id(created.entity_id) is None


def test_create_entity_name_not_null(db_and_repo):
    _, repo = db_and_repo
    with pytest.raises(ValueError):
        repo.create(entity_name=None, entity_revenue=None)  # type: ignore[arg-type]


def test_schema_table_exists_and_columns(db_and_repo):
    db_path, _ = db_and_repo
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.execute("PRAGMA table_info(Entity10)")
    cols = {row["name"] for row in cur.fetchall()}
    conn.close()

    assert {
        "entity_id",
        "entity_name",
        "entity_revenue",
        "entity_creation_date",
        "entity_updated_date",
    }.issubset(cols)
