from __future__ import annotations

import sqlite3
from pathlib import Path

from alembic.config import Config
from alembic import command


EXPECTED_COLUMNS = {
    "Entity6Id",
    "entity_name",
    "entity_revenue",
    "entity_revenue_last2years",
    "entity_creation_date",
    "entity_updated_date",
    "created_by",
    "updated_by",
    "import_source",
    "external_reference",
    "notes",
    "is_deleted",
}

EXPECTED_EXTERNAL_REFERENCE_UNIQUE_INDEXES = {
    # Alembic/SQLite may create either a UNIQUE constraint or a unique index.
    "uq_entity6_external_reference",
    "ix_Entity6_external_reference",
}


def _table_info(conn: sqlite3.Connection, table: str) -> set[str]:
    cur = conn.execute(f"PRAGMA table_info('{table}')")
    rows = cur.fetchall()
    return {r["name"] for r in rows}


def _has_entity6_table(conn: sqlite3.Connection) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        ("Entity6",),
    )
    return cur.fetchone() is not None


def _schema_complete(db_path: str) -> bool:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        if not _has_entity6_table(conn):
            return False

        cols = _table_info(conn, "Entity6")
        if not EXPECTED_COLUMNS.issubset(cols):
            return False

        # Validate external_reference uniqueness exists in some form.
        indexes = conn.execute("PRAGMA index_list('Entity6')").fetchall()
        index_names = {row["name"] for row in indexes}
        if not (EXPECTED_EXTERNAL_REFERENCE_UNIQUE_INDEXES & index_names):
            # If there is a unique constraint but no named index, SQLite still
            # lists it in index_list on recent versions; this is best-effort.
            return False

        return True
    finally:
        conn.close()


def ensure_setup(db_path: str, artifacts_path: str) -> None:
    """Idempotently provision Entity6 schema and write placeholder artifacts."""

    db_path = str(db_path)
    artifacts_path = str(artifacts_path)
    Path(artifacts_path).mkdir(parents=True, exist_ok=True)

    if _schema_complete(db_path):
        Path(artifacts_path, "entity6_schema_ready.txt").write_text(
            "ok", encoding="utf-8"
        )
        return

    # Apply alembic migrations for this project.
    source_root = Path(__file__).resolve().parents[1]
    alembic_ini = source_root / "alembic.ini"
    if not alembic_ini.exists():
        # allow running without alembic.ini in some skeletons
        return

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(source_root / "alembic"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    # If the base table already exists but alembic has no version recorded,
    # stamp at the base revision so upgrade only applies missing column migrations.
    conn_check = sqlite3.connect(db_path)
    conn_check.row_factory = sqlite3.Row
    try:
        table_exists = _has_entity6_table(conn_check)
        has_version = conn_check.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'"
        ).fetchone() is not None
    finally:
        conn_check.close()

    if table_exists and not has_version:
        command.stamp(cfg, "17fdcdd2f161")

    command.upgrade(cfg, "head")

    Path(artifacts_path, "entity6_schema_ready.txt").write_text(
        "ok", encoding="utf-8"
    )
