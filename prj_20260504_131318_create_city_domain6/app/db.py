from __future__ import annotations

import os
import pathlib
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _default_db_path() -> str:
    # Use project root relative path from this module
    project_root = pathlib.Path(__file__).resolve().parent.parent.parent
    return str(project_root / "data" / "app.db")


DB_PATH = os.getenv("APP_DB_PATH", _default_db_path())

# Ensure parent directory exists so sqlite can open the file in tests/lifespan
os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)

engine = create_engine(
    f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
