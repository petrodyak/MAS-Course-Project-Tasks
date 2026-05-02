from __future__ import annotations

import sqlite3


TABLE_NAME = "Entity10"


def ensure_entity10_table(conn: sqlite3.Connection) -> None:
    """Create Entity10 table if it doesn't exist.

    Mirrors the business DDL from the task description:
    - entity_id TEXT PK
    - entity_name NOT NULL
    - entity_revenue nullable REAL (can be negative)
    - creation/updated timestamps default to CURRENT_TIMESTAMP
    - updated timestamp is maintained via trigger on UPDATE
    """

    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            entity_id TEXT PRIMARY KEY NOT NULL,
            entity_name TEXT NOT NULL,
            entity_revenue REAL NULL,
            entity_creation_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            entity_updated_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    conn.execute(
        f"""
        CREATE TRIGGER IF NOT EXISTS {TABLE_NAME}_updated_at
        AFTER UPDATE ON {TABLE_NAME}
        FOR EACH ROW
        BEGIN
            UPDATE {TABLE_NAME}
            SET entity_updated_date = CURRENT_TIMESTAMP
            WHERE entity_id = OLD.entity_id;
        END;
        """
    )

    conn.commit()
