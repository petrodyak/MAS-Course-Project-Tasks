from __future__ import annotations

from pathlib import Path

import pytest

from app.setup import ensure_setup


@pytest.fixture()
def db_and_repo(tmp_path: Path):
    db_path = str(tmp_path / "app.db")
    artifacts_path = str(tmp_path / "artifacts")
    ensure_setup(db_path, artifacts_path)

    from app.entity10_repository import Entity10Repository

    repo = Entity10Repository(db_path=db_path)
    return db_path, repo
