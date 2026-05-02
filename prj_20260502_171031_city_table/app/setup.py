from __future__ import annotations

from pathlib import Path

from app.db import ensure_db_schema


def ensure_setup(db_path: str, artifacts_path: str) -> None:
    """Idempotently ensure DB schema exists and write minimal artifacts."""

    Path(artifacts_path).mkdir(parents=True, exist_ok=True)
    ensure_db_schema(db_path)

    marker = Path(artifacts_path) / "setup_complete.txt"
    marker.write_text(f"ok:{db_path}", encoding="utf-8")
