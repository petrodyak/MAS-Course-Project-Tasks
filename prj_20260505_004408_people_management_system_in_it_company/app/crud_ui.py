from __future__ import annotations
import sqlite3
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from starlette.templating import Jinja2Templates

from pathlib import Path

_templates_dir = Path(__file__).resolve().parent / "templates"
_env = Environment(loader=FileSystemLoader(str(_templates_dir)), cache_size=0)
templates = Jinja2Templates(env=_env)


def _table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [r[1] for r in rows]


def register_crud_ui(app: Any):
    router = APIRouter()

    @app.get("/", response_class=HTMLResponse)
    async def crud_index(request: Request):
        db_path = request.app.state.db_path
        conn = sqlite3.connect(db_path)
        try:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
            table_names = [t[0] for t in tables]
            records: dict[str, list[dict[str, Any]]] = {}
            for t in table_names:
                cols = _table_columns(conn, t)
                cur_rows = conn.execute(
                    f"SELECT {', '.join(cols)} FROM {t} LIMIT 50"
                ).fetchall()
                records[t] = [
                    {cols[i]: row[i] for i in range(len(cols))}
                    for row in cur_rows
                ]
        finally:
            conn.close()

        return templates.TemplateResponse(
            request,
            "index.html",
            {"tables": table_names, "records": records},
        )

    return router
