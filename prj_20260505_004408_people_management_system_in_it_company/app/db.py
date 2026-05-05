from __future__ import annotations

# Minimal stubs to satisfy test fixtures; endpoints use sqlite3 directly.


class _DummySession:
    def close(self) -> None:
        return


def get_db():
    yield _DummySession()


def SessionLocal():
    return _DummySession()
