"""Courses, modules, enrollments, and progress/completion tracking."""
import sqlite3

import pytest

from tests.conftest import AUTH, make_employee


def test_courses_table_exists(db_path):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    with sqlite3.connect(db_path) as conn:
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
    assert "courses" in tables
    assert "course_modules" in tables
    assert "enrollments" in tables


def test_create_course_in_db(db_path):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO courses (course_title, course_description, is_active) "
            "VALUES ('Python 101', 'Intro to Python', 1)"
        )
        row = conn.execute(
            "SELECT course_title FROM courses WHERE course_title = 'Python 101'"
        ).fetchone()
    assert row is not None
    assert row[0] == "Python 101"


def test_course_module_linked_to_course(db_path, seed):
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO courses (course_title, course_description, is_active) "
            "VALUES ('Advanced Go', 'Go deep dive', 1)"
        )
        course_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.execute(
            "INSERT INTO course_modules (course_id, module_title, module_order) "
            "VALUES (?, 'Module 1', 1)",
            (course_id,),
        )
        module_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        row = conn.execute(
            "SELECT course_id FROM course_modules WHERE course_module_id = ?", (module_id,)
        ).fetchone()
    assert row[0] == course_id


def test_course_module_fk_enforced(db_path):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO course_modules (course_id, module_title, module_order) "
                "VALUES (99999, 'Orphan Module', 1)"
            )


def test_enrollment_links_employee_and_course(db_path, seed):
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO courses (course_title, course_description, is_active) "
            "VALUES ('Test Course', 'For enrollment test', 1)"
        )
        course_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.execute(
            "INSERT INTO enrollments (employee_id, course_id, enrolled_at, enrollment_status) "
            "VALUES (?, ?, CURRENT_TIMESTAMP, 'Enrolled')",
            (seed["emp_id"], course_id),
        )
        enroll_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        row = conn.execute(
            "SELECT employee_id, course_id FROM enrollments WHERE enrollment_id = ?",
            (enroll_id,),
        ).fetchone()
    assert row is not None
    assert row[1] == course_id


def test_enrollment_fk_employee_enforced(db_path, seed):
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO enrollments (employee_id, course_id, enrolled_at, enrollment_status) "
                "VALUES (99999, ?, CURRENT_TIMESTAMP, 'Enrolled')",
                (seed["course_id"],),
            )


def test_enrollment_fk_course_enforced(db_path, seed):
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO enrollments (employee_id, course_id, enrolled_at, enrollment_status) "
                "VALUES (?, 99999, CURRENT_TIMESTAMP, 'Enrolled')",
                (seed["emp_id"],),
            )


def test_enrollment_completion_status_update(db_path, seed):
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO courses (course_title, course_description, is_active) VALUES ('Comp', '', 1)"
        )
        course_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.execute(
            "INSERT INTO enrollments (employee_id, course_id, enrolled_at, enrollment_status) "
            "VALUES (?, ?, CURRENT_TIMESTAMP, 'Enrolled')",
            (seed["emp_id"], course_id),
        )
        enroll_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.execute(
            "UPDATE enrollments SET enrollment_status = 'Completed', completed_at = CURRENT_TIMESTAMP "
            "WHERE enrollment_id = ?",
            (enroll_id,),
        )
        row = conn.execute(
            "SELECT enrollment_status FROM enrollments WHERE enrollment_id = ?",
            (enroll_id,),
        ).fetchone()
    assert row[0] == "Completed"


def test_seed_course_exists(db_path, seed):
    """seed fixture must create at least one course."""
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    assert count >= 1, "seed fixture must insert at least one course"
