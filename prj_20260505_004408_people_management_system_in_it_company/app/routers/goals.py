from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.routers.hr_common import execute, fetch_all, fetch_one, get_db_path, require_auth

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("", dependencies=[Depends(require_auth)])
async def list_goals(
    request: Request,
    employee_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
):
    db_path = get_db_path(request)
    query = "SELECT * FROM goals"
    params: list[Any] = []
    if employee_id is not None:
        query += " WHERE employee_id = ?"
        params.append(employee_id)
    query += " ORDER BY goal_id LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    rows = fetch_all(db_path, query, tuple(params))
    return {"items": [dict(r) for r in rows]}


@router.post("", status_code=201, dependencies=[Depends(require_auth)])
async def create_goal(payload: dict[str, Any], request: Request) -> dict[str, Any]:
    db_path = get_db_path(request)
    required = ["employee_id", "owner_user_id", "goal_status", "target_date",
                "measurable_description", "goal_title"]
    missing = [k for k in required if k not in payload]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing fields: {', '.join(missing)}",
        )
    goal_id = execute(
        db_path,
        "INSERT INTO goals (employee_id, owner_user_id, goal_status, target_date, "
        "measurable_description, goal_title) VALUES (?, ?, ?, ?, ?, ?)",
        (
            payload["employee_id"],
            payload["owner_user_id"],
            payload["goal_status"],
            payload["target_date"],
            payload["measurable_description"],
            payload["goal_title"],
        ),
    )
    row = fetch_one(db_path, "SELECT * FROM goals WHERE goal_id = ?", (goal_id,))
    return dict(row) if row else {}
