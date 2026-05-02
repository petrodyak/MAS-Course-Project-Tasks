from __future__ import annotations

import sqlite3


def entity10_table_ddl() -> str:
    # Keep deterministic DDL used by migrations and tests.
    # SQLite stores DATETIME as TEXT; CURRENT_TIMESTAMP is UTC.
    return """
CREATE TABLE IF NOT EXISTS entity10 (
    entity_id TEXT PRIMARY KEY NOT NULL,
    entity_name TEXT NOT NULL,
    entity_revenue REAL NULL,
    entity_creation_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    entity_updated_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS entity10_updated_at
AFTER UPDATE ON entity10
FOR EACH ROW
BEGIN
    UPDATE entity10
    SET entity_updated_date = CURRENT_TIMESTAMP
    WHERE entity_id = OLD.entity_id;
END;
""".strip()


def ensure_entity10_table(conn: sqlite3.Connection) -> None:
    conn.execute(entity10_table_ddl())
    conn.commit()
