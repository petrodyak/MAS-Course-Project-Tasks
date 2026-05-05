from __future__ import annotations
import os
import pathlib
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.crud_ui import register_crud_ui
from app.routers.applicants import router as applicants_router
from app.routers.employees import router as employees_router
from app.routers.goals import router as goals_router
from app.routers.leave_requests import router as leave_requests_router
from app.setup import ensure_setup


@asynccontextmanager
async def lifespan(app: FastAPI):
    _project_root = pathlib.Path(__file__).resolve().parent.parent.parent
    db_path = os.getenv("PEOPLE_DB_PATH", str(_project_root / "data" / "app.db"))
    artifacts_path = os.getenv(
        "PEOPLE_ARTIFACTS_PATH", str(_project_root / "artifacts")
    )
    ensure_setup(db_path, artifacts_path)
    app.state.db_path = db_path
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(employees_router)
app.include_router(applicants_router)
app.include_router(leave_requests_router)
app.include_router(goals_router)
app.include_router(register_crud_ui(app))
