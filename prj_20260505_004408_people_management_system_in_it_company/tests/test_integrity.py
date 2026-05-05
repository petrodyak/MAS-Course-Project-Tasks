"""Data integrity: FK enforcement and NOT NULL constraints."""
import sqlite3

import pytest


def test_fk_applicant_requires_valid_job_posting(db_path):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO applicants (job_posting_id, applicant_first_name, applicant_last_name, applicant_email) "
                "VALUES (99999, 'A', 'B', 'a@b.com')"
            )


def test_fk_team_requires_valid_department(db_path):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO teams (team_name, department_id) VALUES ('X', 99999)"
            )


def test_fk_employee_requires_valid_department(db_path, seed):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO employees (employee_first_name, employee_last_name, employee_middle_name, "
                "employee_work_email, department_id, team_id, current_position_title, legal_status_id, is_terminated) "
                "VALUES ('A','B','C','a@b.com', 99999, 99999, 'Dev', 99999, 0)"
            )


def test_not_null_employee_name(db_path, seed):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    with sqlite3.connect(db_path) as conn:
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO employees (employee_first_name, employee_last_name, employee_middle_name, "
                "employee_work_email, department_id, team_id, current_position_title, legal_status_id, is_terminated) "
                "VALUES (NULL, 'B', 'C', 'a@b.com', ?, ?, 'Dev', ?, 0)",
                (seed["department_id"], seed["team_id"], seed["legal_status_id"]),
            )


def test_not_null_leave_request_status(db_path, seed):
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


def test_all_required_tables_exist(db_path):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    required = {
        "users", "roles", "permissions", "user_roles", "role_permissions",
        "departments", "teams", "legal_statuses", "employees", "employment_assignments",
        "employment_events", "job_postings", "applicants", "applicant_stages",
        "applicant_stage_transitions", "leave_types", "leave_requests", "leave_approvals",
        "performance_review_templates", "performance_reviews", "goals",
        "courses", "course_modules", "enrollments",
        "compensation_salary_bands", "employee_salary_history", "audit_logs",
    }
    with sqlite3.connect(db_path) as conn:
        existing = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
    missing = required - existing
    assert not missing, f"Missing tables: {missing}"
