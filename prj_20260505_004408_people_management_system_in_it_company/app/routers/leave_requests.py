from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.routers.hr_common import execute, fetch_all, fetch_one, get_db_path, require_auth

router = APIRouter(prefix="/leave-requests", tags=["leave_requests"])


@router.get("", dependencies=[Depends(require_auth)])
async def list_leave_requests(
    request: Request,
    employee_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
):
    db_path = get_db_path(request)
    query = "SELECT * FROM leave_requests"
    params: list[Any] = []
    if employee_id is not None:
        query += " WHERE employee_id = ?"
        params.append(employee_id)
    query += " ORDER BY leave_request_id LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    rows = fetch_all(db_path, query, tuple(params))
    return {"items": [dict(r) for r in rows]}


@router.post("", status_code=201, dependencies=[Depends(require_auth)])
async def create_leave_request(payload: dict[str, Any], request: Request) -> dict[str, Any]:
    db_path = get_db_path(request)
    required = ["employee_id", "leave_type_id", "leave_status", "start_date", "end_date",
                "leave_reason", "created_by_user_id"]
    missing = [k for k in required if k not in payload]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing fields: {', '.join(missing)}",
        )
    start = payload["start_date"]
    end = payload["end_date"]
    if end < start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date must not be before start_date",
        )
    lr_id = execute(
        db_path,
        "INSERT INTO leave_requests "
        "(employee_id, leave_type_id, leave_status, start_date, end_date, leave_reason, "
        "created_by_user_id, is_conflicted) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            payload["employee_id"],
            payload["leave_type_id"],
            payload["leave_status"],
            start,
            end,
            payload["leave_reason"],
            payload["created_by_user_id"],
            int(payload.get("is_conflicted", 0)),
        ),
    )
    row = fetch_one(db_path, "SELECT * FROM leave_requests WHERE leave_request_id = ?", (lr_id,))
    return dict(row) if row else {}
