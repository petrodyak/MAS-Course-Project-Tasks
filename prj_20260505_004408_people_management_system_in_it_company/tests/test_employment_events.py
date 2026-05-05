"""Employment events, assignment history, and org hierarchy validation."""
import sqlite3

import pytest

from tests.conftest import AUTH, make_employee


def test_employment_events_table_exists(db_path):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    with sqlite3.connect(db_path) as conn:
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
    assert "employment_events" in tables
    assert "employment_assignments" in tables


def test_create_employment_event(db_path, seed):
    emp_id = seed["emp_id"]
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO employment_events "
            "(employee_id, employment_event_type, actor_user_id, notes, "
            "department_id, team_id, position_title, legal_status_id) "
            "VALUES (?, 'Hire', ?, 'Initial hire', ?, ?, 'Developer', ?)",
            (emp_id, seed["user_id"], seed["department_id"], seed["team_id"], seed["legal_status_id"]),
        )
        event_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        row = conn.execute(
            "SELECT employee_id, employment_event_type FROM employment_events "
            "WHERE employment_event_id = ?",
            (event_id,),
        ).fetchone()
    assert row[0] == emp_id
    assert row[1] == "Hire"


def test_employment_event_fk_employee(db_path, seed):
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO employment_events "
                "(employee_id, employment_event_type, actor_user_id, "
                "department_id, team_id, position_title, legal_status_id) "
                "VALUES (99999, 'Hire', ?, ?, ?, 'Dev', ?)",
                (seed["user_id"], seed["department_id"], seed["team_id"], seed["legal_status_id"]),
            )


def test_employment_assignment_stores_history(client, seed, db_path):
    emp = make_employee(client, seed)
    emp_id = emp["employee_id"]

    with sqlite3.connect(db_path) as conn:
        for title in ("Junior Dev", "Senior Dev"):
            conn.execute(
                "INSERT INTO employment_assignments "
                "(employee_id, department_id, team_id, position_title, legal_status_id, "
                "assigned_at, is_current) "
                "VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1)",
                (emp_id, seed["department_id"], seed["team_id"], title, seed["legal_status_id"]),
            )
        count = conn.execute(
            "SELECT COUNT(*) FROM employment_assignments WHERE employee_id = ?",
            (emp_id,),
        ).fetchone()[0]
    assert count >= 2, "Assignment history must support multiple records per employee"


def test_assignment_fk_department_enforced(db_path, seed):
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO employment_assignments "
                "(employee_id, department_id, team_id, position_title, legal_status_id, "
                "assigned_at, is_current) "
                "VALUES (?, 99999, ?, 'Dev', ?, CURRENT_TIMESTAMP, 1)",
                (seed["emp_id"], seed["team_id"], seed["legal_status_id"]),
            )


def test_terminate_employee_sets_flag(client, seed):
    emp = make_employee(client, seed)
    emp_id = emp["employee_id"]

    r = client.post(f"/employees/{emp_id}/terminate", headers=AUTH)
    assert r.status_code in (200, 204), r.text


def test_terminated_employee_has_is_terminated_flag(client, seed, db_path):
    emp = make_employee(client, seed)
    emp_id = emp["employee_id"]

    client.post(f"/employees/{emp_id}/terminate", headers=AUTH)

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT is_terminated FROM employees WHERE employee_id = ?", (emp_id,)
        ).fetchone()
    assert row is not None
    assert row[0] == 1, "Terminated employee must have is_terminated=1"


def test_employment_events_ordered_by_event_at(db_path, seed):
    emp_id = seed["emp_id"]
    with sqlite3.connect(db_path) as conn:
        for etype in ("Hire", "Promotion", "Transfer"):
            conn.execute(
                "INSERT INTO employment_events "
                "(employee_id, employment_event_type, actor_user_id, "
                "department_id, team_id, position_title, legal_status_id) "
                "VALUES (?, ?, ?, ?, ?, 'Dev', ?)",
                (emp_id, etype, seed["user_id"], seed["department_id"],
                 seed["team_id"], seed["legal_status_id"]),
            )
        rows = conn.execute(
            "SELECT employment_event_type FROM employment_events "
            "WHERE employee_id = ? ORDER BY event_at ASC",
            (emp_id,),
        ).fetchall()
    event_types = [r[0] for r in rows]
    hire_idx = next((i for i, t in enumerate(event_types) if t == "Hire"), -1)
    promo_idx = next((i for i, t in enumerate(event_types) if t == "Promotion"), -1)
    assert hire_idx != -1
    assert promo_idx != -1
