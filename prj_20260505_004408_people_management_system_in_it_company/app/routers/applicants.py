from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from app.routers.hr_common import fetch_all, get_db_path, require_auth

router = APIRouter(prefix="/applicants", tags=["applicants"])


@router.get("", dependencies=[Depends(require_auth)])
async def list_applicants(request: Request, job_posting_id: int | None = None, skip: int = 0, limit: int = 50):
    db_path = get_db_path(request)
    query = "SELECT * FROM applicants"
    params: list[int] = []
    if job_posting_id is not None:
        query += " WHERE job_posting_id = ?"
        params.append(job_posting_id)
    query += " ORDER BY applicant_id LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    rows = fetch_all(db_path, query, tuple(params))
    return {"items": [dict(r) for r in rows]}
