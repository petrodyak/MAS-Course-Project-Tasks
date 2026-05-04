from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

AUTH = {"Authorization": "Bearer test"}


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    return str(tmp_path_factory.mktemp("db") / "test.db")


@pytest.fixture(scope="session")
def test_engine(test_db_path):
    eng = create_engine(
        f"sqlite:///{test_db_path}",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(eng, "connect")
    def _fk_on(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    import app.models.book  # noqa: F401
    import app.models.room  # noqa: F401
    import app.models.shelf  # noqa: F401
    from app.db import Base

    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture(autouse=True)
def clean_tables(test_engine):
    with test_engine.connect() as conn:
        conn.execute(text("DELETE FROM books"))
        conn.execute(text("DELETE FROM shelves"))
        conn.execute(text("DELETE FROM rooms"))
        conn.commit()


@pytest.fixture
def client(test_db_path, test_engine):
    from app.db import get_db
    from app.main import app

    Session = sessionmaker(bind=test_engine)

    def _get_db():
        s = Session()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = _get_db
    app.state.db_path = test_db_path

    c = TestClient(app, raise_server_exceptions=True)
    yield c
    app.dependency_overrides.clear()
