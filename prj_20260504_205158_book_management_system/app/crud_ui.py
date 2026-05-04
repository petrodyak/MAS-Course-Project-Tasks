from __future__ import annotations
import pathlib
import sqlite3

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from starlette.templating import Jinja2Templates

_TEMPLATE_DIR = pathlib.Path(__file__).parent / "templates"
_env = Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)), cache_size=0)
templates = Jinja2Templates(env=_env)

router = APIRouter()


def _rows(conn: sqlite3.Connection, sql: str) -> list[dict]:
    conn.row_factory = sqlite3.Row
    return [dict(r) for r in conn.execute(sql).fetchall()]


@router.get("/", response_class=HTMLResponse)
async def crud_index(request: Request) -> HTMLResponse:
    db_path: str = request.app.state.db_path
    with sqlite3.connect(db_path) as conn:
        rooms = _rows(conn, "SELECT * FROM rooms ORDER BY room_id")
        shelves = _rows(
            conn,
            "SELECT s.*, r.room_name FROM shelves s"
            " JOIN rooms r ON r.room_id = s.room_id"
            " ORDER BY s.shelf_id",
        )
        books = _rows(
            conn,
            "SELECT b.*, s.shelf_name, s.shelf_code, r.room_name"
            " FROM books b"
            " JOIN shelves s ON s.shelf_id = b.shelf_id"
            " JOIN rooms r ON r.room_id = s.room_id"
            " ORDER BY b.book_id",
        )
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "title": "Book Management",
            "rooms": rooms,
            "shelves": shelves,
            "books": books,
        },
    )
