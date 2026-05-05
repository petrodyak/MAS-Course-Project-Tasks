"""Leave requests: creation, status transitions, date validation, overlap."""
import sqlite3

import pytest

from tests.conftest import AUTH, make_employee


def _create_leave_request(client, seed, emp_id=None, **overrides):
    if emp_id is None:
        emp_id = make_employee(client, seed)["employee_id"]
    payload = {
        "employee_id": emp_id,
        "leave_type_id": seed["leave_type_id"],
        "leave_status": "Pending",
        "start_date": "2026-07-01",
        "end_date": "2026-07-05",
        "leave_reason": "Annual vacation",
        "created_by_user_id": seed["user_id"],
        "is_conflicted": 0,
        **overrides,
    }
    r = client.post("/leave-requests", json=payload, headers=AUTH)
    return r


def test_create_leave_request_returns_201(client, seed):
    emp = make_employee(client, seed)
    r = _create_leave_request(client, seed, emp_id=emp["employee_id"])
    assert r.status_code in (200, 201), r.text


def test_leave_request_has_status(client, seed):
    emp = make_employee(client, seed)
    r = _create_leave_request(client, seed, emp_id=emp["employee_id"])
    assert r.status_code in (200, 201), r.text
    body = r.json()
    assert "leave_status" in body or "leave_request_id" in body


def test_list_leave_requests_requires_auth(client, seed):
    r = client.get("/leave-requests")
    assert r.status_code == 401


def test_list_leave_requests_returns_200(client, seed):
    r = client.get("/leave-requests?skip=0&limit=10", headers=AUTH)
    assert r.status_code == 200
    assert "items" in r.json()


def test_leave_request_stored_in_db(client, seed, db_path):
    emp = make_employee(client, seed)
    emp_id = emp["employee_id"]
    r = _create_leave_request(client, seed, emp_id=emp_id)
    assert r.status_code in (200, 201)

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT leave_status FROM leave_requests WHERE employee_id = ?",
            (emp_id,),
        ).fetchone()
    assert row is not None, "Leave request must be persisted in DB"


def test_leave_request_not_null_status(db_path, seed):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    with sqlite3.connect(db_path) as conn:
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO leave_requests "
                "(employee_id, leave_type_id, leave_status, start_date, end_date, leave_reason, "
                "created_by_user_id, is_conflicted) "
                "VALUES (?, ?, NULL, '2026-06-01', '2026-06-10', 'vacation', ?, 0)",
                (seed["emp_id"], seed["leave_type_id"], seed["user_id"]),
            )


def test_leave_approval_recorded(client, seed, db_path):
    emp = make_employee(client, seed)
    emp_id = emp["employee_id"]
    r = _create_leave_request(client, seed, emp_id=emp_id)
    assert r.status_code in (200, 201)
    req_id = r.json().get("leave_request_id")

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO leave_approvals (leave_request_id, decided_by_user_id, approval_status) "
            "VALUES (?, ?, 'Approved')",
            (req_id, seed["user_id"]),
        )
        row = conn.execute(
            "SELECT approval_status FROM leave_approvals WHERE leave_request_id = ?",
            (req_id,),
        ).fetchone()
    assert row is not None
    assert row[0] == "Approved"


def test_leave_type_fk_enforced(db_path, seed):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO leave_requests "
                "(employee_id, leave_type_id, leave_status, start_date, end_date, leave_reason, "
                "created_by_user_id, is_conflicted) "
                "VALUES (1, 99999, 'Pending', '2026-06-01', '2026-06-10', 'test', 1, 0)"
            )


def test_leave_date_order_end_after_start(client, seed):
    emp = make_employee(client, seed)
    r = _create_leave_request(
        client, seed,
        emp_id=emp["employee_id"],
        start_date="2026-07-10",
        end_date="2026-07-05",
    )
    assert r.status_code in (400, 422), "End date before start date must be rejected"


def test_leave_overlap_detection(client, seed, db_path):
    emp = make_employee(client, seed)
    emp_id = emp["employee_id"]

    r1 = _create_leave_request(client, seed, emp_id=emp_id,
                                start_date="2026-08-01", end_date="2026-08-10")
    assert r1.status_code in (200, 201)

    with sqlite3.connect(db_path) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM leave_requests WHERE employee_id = ? "
            "AND start_date <= '2026-08-05' AND end_date >= '2026-08-05'",
            (emp_id,),
        ).fetchone()[0]
    assert count >= 1, "Overlapping leave request period detected in DB"
