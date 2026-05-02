from __future__ import annotations

import sqlite3
from fastapi import APIRouter, Depends, HTTPException, Response

from app.schemas.entity6 import (
    Entity6CreateRequest,
    Entity6Response,
    Entity6UpdateRequest,
)
from app.services.entity6 import Entity6Service, NotFoundError


def get_db_path() -> str:
    # Tester will call app.setup.ensure_setup; router uses env var if present.
    import os

    return os.environ.get("APP_DB_PATH", "data/app.db")


router = APIRouter(prefix="/entity6", tags=["entity6"])


@router.post("", status_code=201, response_model=Entity6Response)
def create_entity6(
    body: Entity6CreateRequest, db_path: str = Depends(get_db_path)
):
    service = Entity6Service(db_path)
    try:
        created = service.create(body.model_dump())
        return Entity6Response(**created)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{entity6_id}", response_model=Entity6Response)
def get_entity6(entity6_id: int, db_path: str = Depends(get_db_path)):
    service = Entity6Service(db_path)
    try:
        row = service.get_by_id(entity6_id)
        return Entity6Response(**row)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Not found")


@router.put("/{entity6_id}", response_model=Entity6Response)
def update_entity6(
    entity6_id: int, body: Entity6UpdateRequest, db_path: str = Depends(get_db_path)
):
    service = Entity6Service(db_path)
    try:
        payload = body.model_dump(exclude_unset=True)
        row = service.update(entity6_id, payload)
        return Entity6Response(**row)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{entity6_id}", status_code=204)
def delete_entity6(entity6_id: int, db_path: str = Depends(get_db_path)):
    service = Entity6Service(db_path)
    deleted = service.delete(entity6_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Not found")
    return Response(status_code=204)
