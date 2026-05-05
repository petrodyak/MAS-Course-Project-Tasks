"""Compensation: salary bands, salary history, current salary lookup."""
import sqlite3

import pytest

from tests.conftest import AUTH, make_employee


def test_compensation_tables_exist(db_path):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    with sqlite3.connect(db_path) as conn:
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
    assert "compensation_salary_bands" in tables
    assert "employee_salary_history" in tables


def test_salary_band_seeded(db_path, seed):
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT salary_band_id FROM compensation_salary_bands LIMIT 1"
        ).fetchone()
    assert row is not None, "At least one salary band must be seeded"


def test_salary_history_linked_to_employee(db_path, seed):
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO employee_salary_history "
            "(employee_id, salary_band_id, base_salary, currency, effective_date, changed_by_user_id, reason) "
            "VALUES (?, ?, 50000, 'USD', '2026-01-01', ?, 'Initial')",
            (seed["emp_id"], seed["salary_band_id"], seed["user_id"]),
        )
        salary_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        row = conn.execute(
            "SELECT employee_id, base_salary FROM employee_salary_history WHERE salary_history_id = ?",
            (salary_id,),
        ).fetchone()
    assert row is not None
    assert row[1] == 50000


def test_salary_history_fk_employee_enforced(db_path, seed):
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO employee_salary_history "
                "(employee_id, salary_band_id, base_salary, currency, effective_date, changed_by_user_id, reason) "
                "VALUES (99999, ?, 60000, 'USD', '2026-01-01', ?, 'Test')",
                (seed["salary_band_id"], seed["user_id"]),
            )


def test_salary_history_fk_band_enforced(db_path, seed):
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO employee_salary_history "
                "(employee_id, salary_band_id, base_salary, currency, effective_date, changed_by_user_id, reason) "
                "VALUES (?, 99999, 60000, 'USD', '2026-01-01', ?, 'Test')",
                (seed["emp_id"], seed["user_id"]),
            )


def test_multiple_salary_records_per_employee(db_path, seed):
    emp_id = seed["emp_id"]
    with sqlite3.connect(db_path) as conn:
        for amount, date in [(50000, "2025-01-01"), (55000, "2025-07-01"), (60000, "2026-01-01")]:
            conn.execute(
                "INSERT INTO employee_salary_history "
                "(employee_id, salary_band_id, base_salary, currency, effective_date, changed_by_user_id, reason) "
                "VALUES (?, ?, ?, 'USD', ?, ?, 'Raise')",
                (emp_id, seed["salary_band_id"], amount, date, seed["user_id"]),
            )
        count = conn.execute(
            "SELECT COUNT(*) FROM employee_salary_history WHERE employee_id = ?",
            (emp_id,),
        ).fetchone()[0]
    assert count >= 3, "Multiple salary history records allowed per employee"


def test_current_salary_is_latest_by_date(db_path, seed):
    emp_id = seed["emp_id"]
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO employee_salary_history "
            "(employee_id, salary_band_id, base_salary, currency, effective_date, changed_by_user_id, reason) "
            "VALUES (?, ?, 45000, 'USD', '2024-01-01', ?, 'Start')",
            (emp_id, seed["salary_band_id"], seed["user_id"]),
        )
        conn.execute(
            "INSERT INTO employee_salary_history "
            "(employee_id, salary_band_id, base_salary, currency, effective_date, changed_by_user_id, reason) "
            "VALUES (?, ?, 70000, 'USD', '2026-06-01', ?, 'Promotion')",
            (emp_id, seed["salary_band_id"], seed["user_id"]),
        )
        current = conn.execute(
            "SELECT base_salary FROM employee_salary_history "
            "WHERE employee_id = ? ORDER BY effective_date DESC LIMIT 1",
            (emp_id,),
        ).fetchone()
    assert current[0] == 70000, "Latest effective_date salary must be 70000"


def test_salary_band_min_max_constraint(db_path, seed):
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT min_salary, max_salary FROM compensation_salary_bands WHERE salary_band_id = ?",
            (seed["salary_band_id"],),
        ).fetchone()
    assert row is not None
    assert row[0] <= row[1], "min_salary must not exceed max_salary in the band"
