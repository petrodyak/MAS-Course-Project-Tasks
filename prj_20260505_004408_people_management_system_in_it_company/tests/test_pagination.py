"""Pagination and filter tests for core list endpoints."""
from tests.conftest import AUTH, make_employee


def _seed_employees(client, seed, count=3):
    ids = []
    for i in range(count):
        emp = make_employee(
            client, seed,
            employee_work_email=f"page_test_{i}@example.com",
            current_position_title=f"Role {i}",
        )
        ids.append(emp["employee_id"])
    return ids


def test_employees_pagination_limit(client, seed):
    _seed_employees(client, seed, count=3)
    r = client.get("/employees?skip=0&limit=2", headers=AUTH)
    assert r.status_code == 200
    assert len(r.json()["items"]) <= 2


def test_employees_pagination_skip(client, seed):
    _seed_employees(client, seed, count=3)
    r_all = client.get("/employees?skip=0&limit=100", headers=AUTH).json()["items"]
    r_skip = client.get("/employees?skip=1&limit=100", headers=AUTH).json()["items"]
    assert len(r_skip) == len(r_all) - 1


def test_employees_filter_by_department(client, seed):
    _seed_employees(client, seed, count=2)
    r = client.get(f"/employees?department_id={seed['department_id']}", headers=AUTH)
    assert r.status_code == 200
    for emp in r.json()["items"]:
        assert emp["department_id"] == seed["department_id"]


def test_employees_filter_by_team(client, seed):
    _seed_employees(client, seed, count=2)
    r = client.get(f"/employees?team_id={seed['team_id']}", headers=AUTH)
    assert r.status_code == 200
    for emp in r.json()["items"]:
        assert emp["team_id"] == seed["team_id"]


def test_employees_filter_no_match_returns_empty(client, seed):
    _seed_employees(client, seed, count=2)
    r = client.get("/employees?department_id=99999", headers=AUTH)
    assert r.status_code == 200
    assert r.json()["items"] == []


def test_applicants_pagination(client, seed):
    r = client.get("/applicants?skip=0&limit=10", headers=AUTH)
    assert r.status_code == 200
    assert "items" in r.json()


def test_applicants_filter_by_job_posting(client, seed, db_path):
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO applicants (job_posting_id, applicant_first_name, applicant_last_name, applicant_email) "
            "VALUES (?, 'Alice', 'Smith', 'alice@example.com')",
            (seed["job_posting_id"],),
        )
    r = client.get(f"/applicants?job_posting_id={seed['job_posting_id']}", headers=AUTH)
    assert r.status_code == 200
    for a in r.json()["items"]:
        assert a["job_posting_id"] == seed["job_posting_id"]


def test_leave_requests_pagination(client, seed):
    r = client.get("/leave-requests?skip=0&limit=10", headers=AUTH)
    assert r.status_code == 200
    assert "items" in r.json()


def test_goals_pagination(client, seed):
    r = client.get("/goals?skip=0&limit=10", headers=AUTH)
    assert r.status_code == 200
    assert "items" in r.json()
