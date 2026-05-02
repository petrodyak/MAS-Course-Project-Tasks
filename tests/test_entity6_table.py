from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.services.entity6 import Entity6Service


@pytest.fixture()
def db_path(tmp_path: Path) -> str:
    return str(tmp_path / "test_entity6.db")


def test_entity6_table_created_on_ensure_setup(db_path: str, tmp_path: Path):
    from app.setup import ensure_setup

    artifacts = tmp_path / "artifacts"
    ensure_setup(db_path, str(artifacts))

    conn = sqlite3.connect(db_path)
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    conn.close()
    assert "Entity6" in tables


def test_entity6_crud_happy_path(db_path: str, tmp_path: Path):
    from app.setup import ensure_setup

    ensure_setup(db_path, str(tmp_path / "artifacts"))
    service = Entity6Service(db_path)

    created = service.create(
        {
            "entity_name": "Acme",
            "entity_revenue": 123.45,
            "entity_revenue_last2years": 50.25,
            "created_by": "user1",
            "updated_by": "user1",
            "import_source": "csv",
            "external_reference": "ext-1",
            "notes": "hello",
        }
    )
    assert created["Entity6Id"] >= 1
    assert created["entity_name"] == "Acme"
    assert float(created["entity_revenue"]) == 123.45
    assert float(created["entity_revenue_last2years"]) == 50.25

    updated = service.update(
        created["Entity6Id"],
        {
            "entity_name": "Acme2",
            "entity_revenue": 200.0,
            "entity_revenue_last2years": 99.0,
        },
    )
    assert updated["entity_name"] == "Acme2"
    assert float(updated["entity_revenue"]) == 200.0
    assert float(updated["entity_revenue_last2years"]) == 99.0

    deleted = service.delete(created["Entity6Id"])
    assert deleted is True

    with pytest.raises(Exception):
        service.get_by_id(created["Entity6Id"])


def test_entity6_external_reference_unique(db_path: str, tmp_path: Path):
    from app.setup import ensure_setup

    ensure_setup(db_path, str(tmp_path / "artifacts"))
    service = Entity6Service(db_path)

    service.create(
        {
            "entity_name": "A",
            "entity_revenue": 1.0,
            "entity_revenue_last2years": 0.5,
            "external_reference": "dup-1",
        }
    )

    with pytest.raises(Exception):
        service.create(
            {
                "entity_name": "B",
                "entity_revenue": 2.0,
                "entity_revenue_last2years": 1.0,
                "external_reference": "dup-1",
            }
        )


def test_entity6_revenue_must_be_finite(db_path: str, tmp_path: Path):
    from app.setup import ensure_setup

    ensure_setup(db_path, str(tmp_path / "artifacts"))
    service = Entity6Service(db_path)

    with pytest.raises(ValueError):
        service.create(
            {
                "entity_name": "A",
                "entity_revenue": float("nan"),
                "entity_revenue_last2years": 0.0,
            }
        )

    with pytest.raises(ValueError):
        service.create(
            {
                "entity_name": "A",
                "entity_revenue": float("inf"),
                "entity_revenue_last2years": 0.0,
            }
        )


def test_entity6_update_non_existent_id_returns_not_found(db_path: str, tmp_path: Path):
    from app.setup import ensure_setup

    ensure_setup(db_path, str(tmp_path / "artifacts"))
    service = Entity6Service(db_path)

    with pytest.raises(Exception):
        service.update(999999, {"entity_name": "X"})


def test_entity6_delete_non_existent_id_returns_false(db_path: str, tmp_path: Path):
    from app.setup import ensure_setup

    ensure_setup(db_path, str(tmp_path / "artifacts"))
    service = Entity6Service(db_path)

    assert service.delete(999999) is False


def test_entity6_update_requires_at_least_one_field(db_path: str, tmp_path: Path):
    from app.setup import ensure_setup

    ensure_setup(db_path, str(tmp_path / "artifacts"))
    service = Entity6Service(db_path)

    created = service.create(
        {
            "entity_name": "A",
            "entity_revenue": 1.0,
            "entity_revenue_last2years": 0.0,
            "external_reference": "u1",
        }
    )

    with pytest.raises(ValueError):
        service.update(created["Entity6Id"], {})
