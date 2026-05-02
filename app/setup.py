from __future__ import annotations

import sqlite3
from pathlib import Path

from app.migration_entity9 import apply_entity9_migration_via_sqlite


def ensure_setup(db_path: str, artifacts_path: str) -> None:
    """Idempotently apply migrations and create any required artifacts."""

    db_path_p = Path(db_path)
    db_path_p.parent.mkdir(parents=True, exist_ok=True)
    artifacts_path_p = Path(artifacts_path)
    artifacts_path_p.mkdir(parents=True, exist_ok=True)

    # Apply entity9 migration DDL (idempotent).
    apply_entity9_migration_via_sqlite(str(db_path_p))

    # Write a tiny artifact marker file.
    marker = artifacts_path_p / "entity9_setup.txt"
    marker.write_text("ok", encoding="utf-8")

    # Verify table exists (hard check so failures are clear).
    conn = sqlite3.connect(str(db_path_p))
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
