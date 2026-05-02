from __future__ import annotations

import os


def ensure_setup(db_path: str, artifacts_path: str) -> None:
    """Idempotently ensure Entity10 schema exists and create marker artifact."""

    # Ensure directory exists so the SQLite file can be created.
    parent = os.path.dirname(os.path.abspath(db_path))
    if parent:
        os.makedirs(parent, exist_ok=True)

    from app.entity10_migrations import apply_entity10_migration

    os.makedirs(artifacts_path, exist_ok=True)
    marker_path = os.path.join(artifacts_path, "entity10_schema.applied")

    # Always apply at DB level; ensures correctness even if marker is stale.
    apply_entity10_migration(db_path)

    # Marker is just for speed/visibility.
    if not os.path.exists(marker_path):
        with open(marker_path, "w", encoding="utf-8") as f:
            f.write("ok\n")
