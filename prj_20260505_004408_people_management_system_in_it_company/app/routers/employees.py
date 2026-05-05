from __future__ import annotations

import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.routers.hr_common import audit_log, execute, fetch_all, fetch_one, get_db_path, require_auth

router = APIRouter(prefix="/employees", tags=["employees"])
ALLOWED_LEGAL_STATUSES = {"Active", "Onboarding", "On Leave", "Terminated", "Terminated"}


def _row_to_employee(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def _validate_legal_status(legal_status_name: str | None) -> None:
    if legal_status_name is not None and legal_status_name not in ALLOWED_LEGAL_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid legal employment status")


@router.get("", dependencies=[Depends(require_auth)])
async def list_employees(request: Request, department_id: int | None = None, team_id: int | None = None, skip: int = 0, limit: int = 50):
    db_path = get_db_path(request)
    query = """
        SELECT e.employee_id, e.employee_first_name, e.employee_last_name,
               e.employee_middle_name, e.employee_work_email, e.employee_phone,
               ea.department_id, ea.team_id, e.current_position_title,
               ea.legal_status_id, e.is_terminated, e.created_at, e.updated_at
        FROM employees e
        JOIN employment_assignments ea ON ea.employee_id = e.employee_id AND ea.is_current = 1
    """
    conditions = []
    params: list[int] = []
    if department_id is not None:
        conditions.append("ea.department_id = ?")
        params.append(department_id)
    if team_id is not None:
        conditions.append("ea.team_id = ?")
        params.append(team_id)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY e.employee_id LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    return {"items": [dict(r) for r in fetch_all(db_path, query, tuple(params))]}


@router.post("", status_code=201, dependencies=[Depends(require_auth)])
async def create_employee(payload: dict[str, Any], request: Request) -> dict[str, Any]:
    db_path = get_db_path(request)
    required = ["employee_first_name", "employee_last_name", "employee_middle_name", "employee_work_email", "department_id", "team_id", "current_position_title", "legal_status_id"]
    missing = [k for k in required if k not in payload]
    if missing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing fields: {', '.join(missing)}")
    employee_id = execute(db_path, "INSERT INTO employees (employee_first_name, employee_last_name, employee_middle_name, employee_work_email, employee_phone, department_id, team_id, current_position_title, legal_status_id, is_terminated, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)", (payload["employee_first_name"], payload["employee_last_name"], payload["employee_middle_name"], payload["employee_work_email"], payload.get("employee_phone"), payload["department_id"], payload["team_id"], payload["current_position_title"], payload["legal_status_id"], int(payload.get("is_terminated", 0))))
    execute(db_path, "INSERT INTO employment_assignments (employee_id, department_id, team_id, position_title, legal_status_id, assigned_at, is_current, created_at) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP)", (employee_id, payload["department_id"], payload["team_id"], payload["current_position_title"], payload["legal_status_id"]))
    row = fetch_one(db_path, "SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
    return dict(row) if row else {}


@router.put("/{employee_id}", dependencies=[Depends(require_auth)])
async def update_employee(employee_id: int, payload: dict[str, Any], request: Request) -> dict[str, Any]:
    db_path = get_db_path(request)
    row = fetch_one(db_path, "SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
    if row is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    mutable = {k: payload.get(k, row[k]) for k in ["employee_first_name", "employee_last_name", "employee_middle_name", "employee_work_email", "employee_phone", "department_id", "team_id", "current_position_title", "legal_status_id", "is_terminated"]}
    legal_status_name = payload.get("legal_status_name")
    _validate_legal_status(legal_status_name)
          # Ensure employee_id is immutable
    if payload.get("employee_id") is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="employee_id is immutable and cannot be changed")
    if payload.get("employee_id") is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="employee_id is immutable and cannot be changed")
    execute(db_path, "UPDATE employees SET employee_first_name = ?, employee_last_name = ?, employee_middle_name = ?, employee_work_email = ?, employee_phone = ?, department_id = ?, team_id = ?, current_position_title = ?, legal_status_id = ?, is_terminated = ?, updated_at = CURRENT_TIMESTAMP WHERE employee_id = ?", (*mutable.values(), employee_id))
    if any(key in payload for key in {"department_id", "team_id", "current_position_title", "legal_status_id", "legal_status_name"}):
        execute(db_path, "UPDATE employment_assignments SET is_current = 0, unassigned_at = CURRENT_TIMESTAMP WHERE employee_id = ? AND is_current = 1", (employee_id,))
        execute(db_path, "INSERT INTO employment_assignments (employee_id, department_id, team_id, position_title, legal_status_id, assigned_at, is_current, created_at) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP)", (employee_id, mutable["department_id"], mutable["team_id"], mutable["current_position_title"], mutable["legal_status_id"]))
    audit_log(db_path, int(payload.get("actor_user_id", 1)), "employees", employee_id, "update", mutable)
    return dict(fetch_one(db_path, "SELECT * FROM employees WHERE employee_id = ?", (employee_id,)))


@router.post("/{employee_id}/terminate", dependencies=[Depends(require_auth)])
async def terminate_employee(employee_id: int, request: Request) -> dict[str, Any]:
    db_path = get_db_path(request)
    execute(db_path, "UPDATE employees SET is_terminated = 1, legal_status_id = 1, updated_at = CURRENT_TIMESTAMP WHERE employee_id = ?", (employee_id,))
    return {"employee_id": employee_id, "is_terminated": True}


@router.post("/{employee_id}/deactivate", dependencies=[Depends(require_auth)])
async def deactivate_employee(employee_id: int, request: Request) -> dict[str, Any]:
    db_path = get_db_path(request)
    execute(db_path, "UPDATE employees SET is_terminated = 0, updated_at = CURRENT_TIMESTAMP WHERE employee_id = ?", (employee_id,))
    return {"employee_id": employee_id, "is_terminated": False}
