"""RBAC: verify HR endpoints require Authorization header."""
import pytest
from tests.conftest import AUTH


@pytest.mark.parametrize("path", ["/employees", "/applicants", "/leave-requests", "/goals"])
def test_list_endpoints_require_auth(client, seed, path):
    r = client.get(path)
    assert r.status_code == 401, f"{path} must return 401 without Authorization header"


def test_list_employees_with_valid_token(client, seed):
    r = client.get("/employees", headers=AUTH)
    assert r.status_code == 200


def test_create_employee_requires_auth(client, seed):
    r = client.post("/employees", json={
        "employee_first_name": "A", "employee_last_name": "B",
        "employee_middle_name": "C", "employee_work_email": "a@b.com",
        "department_id": seed["department_id"], "team_id": seed["team_id"],
        "current_position_title": "Dev", "legal_status_id": seed["legal_status_id"],
    })
    assert r.status_code == 401


def test_update_employee_requires_auth(client, seed):
    from tests.conftest import make_employee
    emp = make_employee(client, seed)
    r = client.put(f"/employees/{emp['employee_id']}", json={"current_position_title": "X"})
    assert r.status_code == 401


def test_terminate_employee_requires_auth(client, seed):
    from tests.conftest import make_employee
    emp = make_employee(client, seed)
    r = client.post(f"/employees/{emp['employee_id']}/terminate")
    assert r.status_code == 401


def test_rbac_schema_supports_roles_permissions(db_path):
    """Verify the RBAC schema tables exist and FK relationships hold."""
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        from app.setup import ensure_setup
        ensure_setup(db_path, "/tmp/artifacts")
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
    assert "roles" in tables
    assert "permissions" in tables
    assert "user_roles" in tables
    assert "role_permissions" in tables


def test_rbac_permission_lookup_via_db(db_path, seed):
    """Verify a seeded user can be found to have a permission via join query."""
    from app.setup import ensure_setup
    ensure_setup(db_path, "/tmp/artifacts")
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("""
            SELECT p.permission_key
            FROM permissions p
            JOIN role_permissions rp ON rp.permission_id = p.permission_id
            JOIN user_roles      ur ON ur.role_id         = rp.role_id
            JOIN users           u  ON u.user_id          = ur.user_id
            WHERE u.user_email = 'admin@test.com' AND p.permission_key = 'hr.employees.write'
        """).fetchone()
    assert row is not None, "Seeded admin user must have hr.employees.write permission via role"
