"""Audit log: verify audit_logs rows are created on mutations."""
import json
import sqlite3

from tests.conftest import AUTH, make_employee


def test_audit_log_created_on_employee_update(client, seed):
    emp = make_employee(client, seed)
    emp_id = emp["employee_id"]

    client.put(
        f"/employees/{emp_id}",
        json={"current_position_title": "Senior Dev"},
        headers=AUTH,
    )

    with sqlite3.connect(client.app.state.db_path) as conn:
        row = conn.execute(
            "SELECT * FROM audit_logs WHERE entity_type = 'employees' AND entity_id = ? AND change_action = 'update'",
            (emp_id,),
        ).fetchone()
    assert row is not None, "audit_logs must have a row after employee update"


def test_audit_log_has_changed_fields(client, seed):
    emp = make_employee(client, seed)
    emp_id = emp["employee_id"]

    client.put(
        f"/employees/{emp_id}",
        json={"current_position_title": "Lead"},
        headers=AUTH,
    )

    with sqlite3.connect(client.app.state.db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM audit_logs WHERE entity_type = 'employees' AND entity_id = ?",
            (emp_id,),
        ).fetchone()
    assert row is not None
    fields = json.loads(row["changed_fields_json"])
    assert isinstance(fields, dict), "changed_fields_json must be a JSON object"


def test_audit_log_has_actor_and_timestamp(client, seed):
    emp = make_employee(client, seed)
    emp_id = emp["employee_id"]

    client.put(f"/employees/{emp_id}", json={"current_position_title": "X"}, headers=AUTH)

    with sqlite3.connect(client.app.state.db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM audit_logs WHERE entity_type = 'employees' AND entity_id = ?",
            (emp_id,),
        ).fetchone()
    assert row["actor_user_id"] is not None
    assert row["created_at"] is not None


def test_audit_log_table_exists(db_path):
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    with sqlite3.connect(db_path) as conn:
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
    assert "audit_logs" in tables
