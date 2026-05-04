from __future__ import annotations

import os
import pathlib
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers.books import router as books_router
from app.routers.rooms import router as rooms_router
from app.routers.shelves import router as shelves_router
from app.setup import ensure_setup


@asynccontextmanager
async def lifespan(app: FastAPI):
    _project_root = pathlib.Path(__file__).resolve().parent.parent.parent
    db_path = os.getenv("BOOK_DB_PATH", str(_project_root / "data" / "app.db"))
    artifacts_path = os.getenv(
        "BOOK_ARTIFACTS_PATH", str(_project_root / "artifacts")
    )
    ensure_setup(db_path, artifacts_path)
    app.state.db_path = db_path
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(rooms_router)
app.include_router(shelves_router)
app.include_router(books_router)
