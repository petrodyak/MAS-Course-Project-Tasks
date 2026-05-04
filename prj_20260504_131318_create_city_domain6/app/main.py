from __future__ import annotations

import os
import pathlib
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers.cities import router as cities_router
from app.setup import ensure_setup


@asynccontextmanager
async def lifespan(app: FastAPI):
    _project_root = pathlib.Path(__file__).resolve().parent.parent.parent
    db_path = os.getenv("APP_DB_PATH", str(_project_root / "data" / "app.db"))
    artifacts_path = os.getenv(
        "APP_ARTIFACTS_PATH", str(_project_root / "artifacts")
    )
    ensure_setup(db_path, artifacts_path)
    app.state.db_path = db_path
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(cities_router)
