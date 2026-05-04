from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from starlette.templating import Jinja2Templates

_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)


def register_crud_ui(app):
    router = APIRouter()

    @app.get("/", response_class=HTMLResponse)
    async def crud_index(request: Request):
        db_path = request.app.state.db_path
        import sqlite3

        conn = sqlite3.connect(db_path)
        try:
            rows = conn.execute(
                "SELECT city_id, city_name, city_old_name, city_size_km2, country, established_date FROM city ORDER BY city_id"
            ).fetchall()
            records: list[dict[str, Any]] = [
                {
                    "city_id": r[0],
                    "city_name": r[1],
                    "city_old_name": r[2],
                    "city_size_km2": r[3],
                    "country": r[4],
                    "established_date": r[5],
                }
                for r in rows
            ]
        finally:
            conn.close()

        return templates.TemplateResponse(request, "city.html", {"records": records})

    return router
