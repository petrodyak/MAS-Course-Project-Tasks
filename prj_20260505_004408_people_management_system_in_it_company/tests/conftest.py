import os
import pathlib
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.db import SessionLocal, get_db
from app.main import app
from app.setup import ensure_setup

AUTH = {"Authorization": "Bearer test"}


@pytest.fixture(scope="session")
def source_path() -> str:
    return str(pathlib.Path(__file__).resolve().parent.parent)


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "data" / "app.db")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


@pytest.fixture
def client(db_path):
    ensure_setup(db_path, str(pathlib.Path(db_path).parent.parent / "artifacts"))
    os.environ["PEOPLE_DB_PATH"] = db_path

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    os.environ.pop("PEOPLE_DB_PATH", None)


@pytest.fixture
def seed(db_path):
    """Seed required FK rows used across all HR tests."""
    ensure_setup(db_path, str(pathlib.Path(db_path).parent.parent / "artifacts"))
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO users (user_email, user_password_hash, is_active) VALUES ('admin@test.com', 'x', 1)"
        )
        user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            "INSERT INTO legal_statuses (legal_status_name, legal_status_description, is_active) VALUES ('Full-time', 'Full-time employee', 1)"
        )
        ls_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute("INSERT INTO departments (department_name) VALUES ('Engineering')")
        dept_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            "INSERT INTO departments (department_name) VALUES ('Product')"
        )
        dept2_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            "INSERT INTO teams (team_name, department_id) VALUES ('Backend', ?)", (dept_id,)
        )
        team_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            "INSERT INTO teams (team_name, department_id) VALUES ('Frontend', ?)", (dept_id,)
        )
        team2_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            "INSERT INTO roles (role_name, role_description, is_active) VALUES ('HR Admin', 'HR module admin', 1)"
        )
        role_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            "INSERT INTO permissions (permission_key, permission_description, is_active) VALUES ('hr.employees.write', 'Write HR employees', 1)"
        )
        perm_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            "INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)", (role_id, perm_id)
        )
        conn.execute(
            "INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id)
        )
        conn.execute(
            "INSERT INTO leave_types (leave_type_name, leave_type_description, is_active) VALUES ('Annual', 'Annual leave', 1)"
        )
        leave_type_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            "INSERT INTO performance_review_templates (template_name, template_description) VALUES ('Annual Review', 'Standard annual review')"
        )
        template_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            "INSERT INTO compensation_salary_bands (band_name, min_salary, max_salary, currency) VALUES ('L3', 60000, 90000, 'USD')"
        )
        band_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            "INSERT INTO courses (course_title, course_description, is_active) VALUES ('Python Basics', 'Intro to Python', 1)"
        )
        course_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            "INSERT INTO job_postings (job_title, job_description, location, is_active) VALUES ('Backend Dev', 'Build APIs', 'Remote', 1)"
        )
        posting_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            "INSERT INTO employees (employee_first_name, employee_last_name, employee_middle_name, "
            "employee_work_email, department_id, team_id, current_position_title, legal_status_id, is_terminated) "
            "VALUES ('Seed', 'Employee', 'N', 'seed@example.com', ?, ?, 'Dev', ?, 0)",
            (dept_id, team_id, ls_id),
        )
        emp_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    return {
        "user_id": user_id,
        "legal_status_id": ls_id,
        "department_id": dept_id,
        "department2_id": dept2_id,
        "team_id": team_id,
        "team2_id": team2_id,
        "role_id": role_id,
        "perm_id": perm_id,
        "leave_type_id": leave_type_id,
        "template_id": template_id,
        "band_id": band_id,
        "course_id": course_id,
        "job_posting_id": posting_id,
        "emp_id": emp_id,
        "salary_band_id": band_id,
    }


def make_employee(client, seed, **overrides):
    """Helper: create an employee using seeded FK ids."""
    payload = {
        "employee_first_name": "Test",
        "employee_last_name": "User",
        "employee_middle_name": "M",
        "employee_work_email": f"user{id(overrides)}@example.com",
        "department_id": seed["department_id"],
        "team_id": seed["team_id"],
        "current_position_title": "Developer",
        "legal_status_id": seed["legal_status_id"],
    }
    payload.update(overrides)
    r = client.post("/employees", json=payload, headers=AUTH)
    assert r.status_code == 201, r.text
    return r.json()
