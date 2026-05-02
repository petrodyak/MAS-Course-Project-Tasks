from __future__ import annotations

import os

from fastapi import FastAPI

from app.routers.entity6 import router as entity6_router


def create_app() -> FastAPI:
    app = FastAPI(title="Entity6 API")
    app.include_router(entity6_router)
    return app


app = create_app()

# For convenience during local dev/tests.
os.environ.setdefault("APP_DB_PATH", "data/app.db")
