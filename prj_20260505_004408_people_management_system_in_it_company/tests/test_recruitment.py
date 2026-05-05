"""Job postings and applicants: FK linkage and stage transitions."""
import sqlite3

import pytest


def test_job_posting_applicant_linkage(db_path, seed):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO applicants (job_posting_id, applicant_first_name, applicant_last_name, applicant_email) "
            "VALUES (?, 'Jane', 'Doe', 'jane@example.com')",
            (seed["job_posting_id"],),
        )
        applicant_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        row = conn.execute(
            "SELECT job_posting_id FROM applicants WHERE applicant_id = ?", (applicant_id,)
        ).fetchone()
    assert row[0] == seed["job_posting_id"], "Applicant must be linked to its job posting"


def test_applicant_requires_valid_job_posting_fk(db_path, seed):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO applicants (job_posting_id, applicant_first_name, applicant_last_name, applicant_email) "
                "VALUES (99999, 'X', 'Y', 'x@y.com')"
            )


def test_applicant_stage_transition_records_timestamp(db_path, seed):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO applicants (job_posting_id, applicant_first_name, applicant_last_name, applicant_email) "
            "VALUES (?, 'Bob', 'Jones', 'bob@example.com')",
            (seed["job_posting_id"],),
        )
        applicant_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.execute(
            "INSERT INTO applicant_stages (applicant_id, stage_name, stage_started_at, performed_by_user_id) "
            "VALUES (?, 'Screening', CURRENT_TIMESTAMP, ?)",
            (applicant_id, seed["user_id"]),
        )
        stage_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.execute(
            "INSERT INTO applicant_stage_transitions "
            "(applicant_stage_id, from_stage_name, to_stage_name, transitioned_at, performed_by_user_id) "
            "VALUES (?, 'Screening', 'Interview', CURRENT_TIMESTAMP, ?)",
            (stage_id, seed["user_id"]),
        )

        row = conn.execute(
            "SELECT transitioned_at, performed_by_user_id FROM applicant_stage_transitions "
            "WHERE applicant_stage_id = ?",
            (stage_id,),
        ).fetchone()
    assert row is not None, "Stage transition must be recorded"
    assert row[0] is not None, "transitioned_at must be set"
    assert row[1] == seed["user_id"], "performed_by_user_id must match"


def test_multiple_applicants_for_same_posting(db_path, seed):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    with sqlite3.connect(db_path) as conn:
        for i in range(3):
            conn.execute(
                "INSERT INTO applicants (job_posting_id, applicant_first_name, applicant_last_name, applicant_email) "
                "VALUES (?, 'App', ?, ?)",
                (seed["job_posting_id"], f"No{i}", f"app{i}@example.com"),
            )
        count = conn.execute(
            "SELECT COUNT(*) FROM applicants WHERE job_posting_id = ?",
            (seed["job_posting_id"],),
        ).fetchone()[0]
    assert count >= 3, "Multiple applicants can share the same job posting"
