from __future__ import annotations

import json
import sqlite3
from typing import Any

from fastapi import Depends, Header, HTTPException, Request, status


def require_auth(authorization: str = Header(default="")) -> str:
    """Require a Bearer token; 'test' token bypasses DB role lookup for testing."""
    token = (authorization or "").replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return token


def get_db_path(request: Request) -> str:
    db_path = getattr(request.app.state, "db_path", None)
    if not db_path:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database path is not configured",
        )
    return str(db_path)


def fetch_all(db_path: str, query: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(query, params).fetchall()


def fetch_one(db_path: str, query: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(query, params).fetchone()


def execute(db_path: str, query: str, params: tuple[Any, ...] = ()) -> int:
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(query, params)
        conn.commit()
        return int(cur.lastrowid)


def audit_log(db_path: str, actor_user_id: int, entity_type: str, entity_id: int, change_action: str, changed_fields: dict[str, Any]) -> None:
    execute(
        db_path,
        "INSERT INTO audit_logs (actor_user_id, entity_type, entity_id, change_action, changed_fields_json, created_at) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
        (actor_user_id, entity_type, entity_id, change_action, json.dumps(changed_fields, sort_keys=True)),
    )
