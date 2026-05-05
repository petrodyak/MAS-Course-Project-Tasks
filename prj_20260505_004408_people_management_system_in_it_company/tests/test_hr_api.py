import sqlite3

import pytest

from tests.conftest import AUTH, make_employee


@pytest.mark.parametrize(
    "path",
    ["/employees", "/applicants", "/leave-requests", "/goals"],
)
def test_list_routes_exist(client, seed, path):
    response = client.get(path, headers=AUTH)
    assert response.status_code == 200
    assert "items" in response.json()


def test_employee_id_is_immutable(client, seed):
    emp = make_employee(client, seed)
    emp_id = emp["employee_id"]
    r = client.put(
        f"/employees/{emp_id}",
        json={"employee_id": 9999, "current_position_title": "Updated"},
        headers=AUTH,
    )
    assert r.status_code == 400
    assert "immutable" in r.json()["detail"].lower()


def test_employee_create_update_and_terminate(client, seed):
    emp = make_employee(client, seed)
    emp_id = emp["employee_id"]

    updated = client.put(
        f"/employees/{emp_id}",
        json={"current_position_title": "Senior Developer"},
        headers=AUTH,
    )
    assert updated.status_code == 200
    assert updated.json()["current_position_title"] == "Senior Developer"
    assert updated.json()["employee_id"] == emp_id

    # Verify audit log was created by the update
    with sqlite3.connect(client.app.state.db_path) as conn:
        row = conn.execute(
            "SELECT * FROM audit_logs WHERE entity_type = 'employees' AND entity_id = ?",
            (emp_id,),
        ).fetchone()
    assert row is not None, "Audit log must be written on employee update"

    term = client.post(f"/employees/{emp_id}/terminate", headers=AUTH)
    assert term.status_code == 200
    assert term.json()["is_terminated"] is True

    deactivate = client.post(f"/employees/{emp_id}/deactivate", headers=AUTH)
    assert deactivate.status_code == 200
    assert deactivate.json()["is_terminated"] is False


def test_employee_org_assignment_history_preserved(client, seed):
    emp = make_employee(client, seed)
    emp_id = emp["employee_id"]

    update = client.put(
        f"/employees/{emp_id}",
        json={
            "department_id": seed["department2_id"],
            "team_id": seed["team2_id"],
            "current_position_title": "Lead Developer",
        },
        headers=AUTH,
    )
    assert update.status_code == 200

    after = client.get("/employees", params={"department_id": seed["department2_id"]}, headers=AUTH).json()
    assert any(item["employee_id"] == emp_id for item in after["items"])

    with sqlite3.connect(client.app.state.db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT department_id, team_id, position_title, is_current "
            "FROM employment_assignments WHERE employee_id = ? ORDER BY employment_assignment_id",
            (emp_id,),
        ).fetchall()
    assert len(rows) >= 2, "Prior assignment history must be preserved"
    assert rows[0]["is_current"] == 0
    assert rows[-1]["is_current"] == 1
    assert rows[0]["department_id"] == seed["department_id"]
    assert rows[-1]["department_id"] == seed["department2_id"]
