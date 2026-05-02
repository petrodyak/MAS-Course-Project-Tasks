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


def test_create_requires_entity_name_not_null(db_and_repo):
    _, repo = db_and_repo

    with pytest.raises(ValueError) as exc:
        repo.create(entity_name=None, entity_revenue=None)  # type: ignore[arg-type]
    assert "cannot be NULL" in str(exc.value)


def test_create_accepts_negative_and_null_revenue(db_and_repo):
    _, repo = db_and_repo

    r1 = repo.create(entity_name="A", entity_revenue=-10.5)
    assert r1.entity_revenue == -10.5
    assert r1.entity_creation_date == r1.entity_updated_date

    r2 = repo.create(entity_name="B", entity_revenue=None)
    assert r2.entity_revenue is None


def test_update_changes_updated_timestamp_but_not_creation(db_and_repo):
    _, repo = db_and_repo

    r1 = repo.create(entity_name="X", entity_revenue=1.0)
    r2 = repo.update(
        r1.entity_id,
        entity_name="Y",
        entity_revenue=2.0,
    )
    assert r2 is not None
    assert r2.entity_id == r1.entity_id
    assert r2.entity_creation_date == r1.entity_creation_date
    assert r2.entity_updated_date != r1.entity_updated_date


def test_update_returns_none_when_missing(db_and_repo):
    _, repo = db_and_repo

    res = repo.update(
        "missing-id",
        entity_name="Z",
        entity_revenue=None,
    )
    assert res is None


def test_delete_removes_record(db_and_repo):
    _, repo = db_and_repo

    r1 = repo.create(entity_name="Del", entity_revenue=None)
    ok = repo.delete(r1.entity_id)
    assert ok is True
    assert repo.get_by_id(r1.entity_id) is None

    ok2 = repo.delete(r1.entity_id)
    assert ok2 is False


def test_schema_column_names(db_and_repo):
    db_path, _ = db_and_repo
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.execute("PRAGMA table_info(Entity10)")
    columns = {row["name"] for row in cur.fetchall()}
    conn.close()

    assert {
        "entity_id",
        "entity_name",
        "entity_revenue",
        "entity_creation_date",
        "entity_updated_date",
    }.issubset(columns)


def test_schema_column_types(db_and_repo):
    db_path, _ = db_and_repo
    conn = sqlite3.connect(db_path)
    cur = conn.execute("PRAGMA table_info(Entity10)")
    types = {row[1]: row[2].upper() for row in cur.fetchall()}
    conn.close()

    assert types["entity_id"].startswith("TEXT")
    assert types["entity_name"].startswith("TEXT")
    assert types["entity_revenue"].startswith("REAL")
    assert types["entity_creation_date"].startswith("TEXT")
    assert types["entity_updated_date"].startswith("TEXT")


def test_migration_idempotent(tmp_path):
    db_path = str(tmp_path / "test.db")
    artifacts_path = str(tmp_path / "artifacts")

    from app.setup import ensure_setup

    ensure_setup(db_path, artifacts_path)
    ensure_setup(db_path, artifacts_path)

    conn = sqlite3.connect(db_path)
    tables = [
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    ]
    conn.close()

    assert "Entity10" in tables
