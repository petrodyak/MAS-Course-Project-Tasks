from __future__ import annotations
import os
import pathlib
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


_project_root = pathlib.Path(__file__).resolve().parent.parent


def _default_db_path() -> str:
    return str(_project_root / "data" / "app.db")


DB_PATH = os.getenv("BOOK_MGMT_DB_PATH", _default_db_path())


def get_db_url() -> str:
    return f"sqlite:///{DB_PATH}"


engine = create_engine(
    get_db_url(), connect_args={"check_same_thread": False}
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _connection_record):
    dbapi_conn.execute("PRAGMA foreign_keys=ON")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
