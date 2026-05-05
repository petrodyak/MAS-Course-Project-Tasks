import sqlite3

from fastapi.testclient import TestClient


def _seed_fk_tables(db_path: str):
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO legal_statuses (
                legal_status_name,
                legal_status_description,
                is_active,
                created_at,
                updated_at
            ) VALUES ('Active','desc',1,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)
            """
        )
        legal_status_id = conn.execute(
            "SELECT legal_status_id FROM legal_statuses"
        ).fetchone()[0]
        conn.execute(
            """
            INSERT INTO departments (department_name, created_at, updated_at)
            VALUES ('Dev', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
        )
        department_id = conn.execute(
            "SELECT department_id FROM departments"
        ).fetchone()[0]
        conn.execute(
            """
            INSERT INTO teams (team_name, department_id, created_at, updated_at)
            VALUES ('Backend', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (department_id,),
        )
        team_id = conn.execute("SELECT team_id FROM teams").fetchone()[0]
    return legal_status_id, department_id, team_id


def test_employee_created_and_appears_in_ui(client: TestClient):
    db_path = client.app.state.db_path
    legal_status_id, department_id, team_id = _seed_fk_tables(db_path)

    r = client.post(
        "/employees",
        json={
            "employee_first_name": "John",
            "employee_last_name": "Doe",
            "employee_middle_name": "M",
            "employee_work_email": "john.doe@example.com",
            "employee_phone": "123",
            "department_id": department_id,
            "team_id": team_id,
            "current_position_title": "Backend Dev",
            "legal_status_id": legal_status_id,
        },
        headers={"Authorization": "Bearer test"},
    )
    assert r.status_code == 201

    page = client.get("/")
    assert page.status_code == 200
    assert "John" in page.text
    assert "Doe" in page.text
