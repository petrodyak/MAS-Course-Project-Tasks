"""Performance reviews and goals: creation, FK linkage, list endpoints."""
import sqlite3

import pytest

from tests.conftest import AUTH, make_employee


def _insert_review(conn, seed, emp_id):
    conn.execute(
        "INSERT INTO performance_reviews "
        "(employee_id, review_template_id, reviewer_user_id, due_date) "
        "VALUES (?, ?, ?, '2026-12-31')",
        (emp_id, seed["template_id"], seed["user_id"]),
    )
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def test_create_performance_review_in_db(client, seed, db_path):
    emp = make_employee(client, seed)
    emp_id = emp["employee_id"]

    with sqlite3.connect(db_path) as conn:
        review_id = _insert_review(conn, seed, emp_id)
        row = conn.execute(
            "SELECT employee_id FROM performance_reviews WHERE performance_review_id = ?",
            (review_id,),
        ).fetchone()
    assert row is not None
    assert row[0] == emp_id


def test_performance_review_fk_employee(db_path, seed):
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO performance_reviews "
                "(employee_id, review_template_id, reviewer_user_id, due_date) "
                "VALUES (99999, ?, ?, '2026-12-31')",
                (seed["template_id"], seed["user_id"]),
            )


def test_list_goals_requires_auth(client, seed):
    r = client.get("/goals")
    assert r.status_code == 401


def test_list_goals_returns_200(client, seed):
    r = client.get("/goals?skip=0&limit=10", headers=AUTH)
    assert r.status_code == 200
    assert "items" in r.json()


def test_create_goal_and_retrieve(client, seed, db_path):
    emp = make_employee(client, seed)
    emp_id = emp["employee_id"]

    payload = {
        "employee_id": emp_id,
        "goal_title": "Improve code quality",
        "measurable_description": "Reduce bugs by 30%",
        "target_date": "2026-12-31",
        "goal_status": "Active",
        "owner_user_id": seed["user_id"],
    }
    r = client.post("/goals", json=payload, headers=AUTH)
    assert r.status_code in (200, 201), r.text

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT goal_title FROM goals WHERE employee_id = ?",
            (emp_id,),
        ).fetchone()
    assert row is not None
    assert row[0] == "Improve code quality"


def test_goal_fk_employee_required(db_path, seed):
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO goals "
                "(employee_id, owner_user_id, goal_status, target_date, measurable_description, goal_title) "
                "VALUES (99999, ?, 'Active', '2026-12-31', 'desc', 'Goal')",
                (seed["user_id"],),
            )


def test_multiple_goals_per_employee(client, seed, db_path):
    emp = make_employee(client, seed)
    emp_id = emp["employee_id"]

    for i in range(3):
        payload = {
            "employee_id": emp_id,
            "goal_title": f"Goal {i}",
            "measurable_description": f"Measure {i}",
            "target_date": "2026-12-31",
            "goal_status": "Active",
            "owner_user_id": seed["user_id"],
        }
        client.post("/goals", json=payload, headers=AUTH)

    with sqlite3.connect(db_path) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM goals WHERE employee_id = ?", (emp_id,)
        ).fetchone()[0]
    assert count >= 3


def test_performance_review_template_exists(db_path, seed):
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT review_template_id FROM performance_review_templates LIMIT 1"
        ).fetchone()
    assert row is not None, "At least one performance review template must be seeded"
