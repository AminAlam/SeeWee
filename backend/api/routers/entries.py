from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from api.db import db_session
from core.repos.entries_repo import EntriesRepo, EntryRecord
from core.entry_schemas import (
    ENTRY_TYPES,
    get_all_schemas_for_ui,
    normalize_entry,
    validate_entry,
)

router = APIRouter(prefix="/entries", tags=["entries"])


class EntryCreateIn(BaseModel):
    type: str = Field(min_length=1)
    data: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class EntryUpdateIn(BaseModel):
    data: dict[str, Any] | None = None
    tags: list[str] | None = None


class EntryOut(BaseModel):
    id: str
    type: str
    data: dict[str, Any]
    tags: list[str]
    created_at: str
    updated_at: str


def _to_out(r: EntryRecord) -> EntryOut:
    return EntryOut(
        id=r.id,
        type=r.type,
        data=r.data,
        tags=r.tags,
        created_at=r.created_at.isoformat(),
        updated_at=r.updated_at.isoformat(),
    )


@router.get("/types")
def list_entry_types() -> dict[str, Any]:
    """Return all entry type schemas for UI form generation."""
    return {
        "types": ENTRY_TYPES,
        "schemas": get_all_schemas_for_ui(),
    }


@router.get("")
def list_entries(
    entry_type: str | None = None,
    db: Session = Depends(db_session),
) -> list[EntryOut]:
    repo = EntriesRepo(db)
    return [_to_out(r) for r in repo.list(entry_type=entry_type)]


@router.post("")
def create_entry(payload: EntryCreateIn, db: Session = Depends(db_session)) -> EntryOut:
    # Validate against schema (non-blocking, just logs warnings for now)
    is_valid, errors = validate_entry(payload.type, payload.data)
    if not is_valid:
        # For MVP, we still accept the data but could optionally reject
        # raise HTTPException(status_code=400, detail={"validation_errors": errors})
        pass

    repo = EntriesRepo(db)
    rec = repo.create(entry_type=payload.type, data=payload.data, tags=payload.tags)
    return _to_out(rec)


@router.get("/{entry_id}")
def get_entry(entry_id: str, db: Session = Depends(db_session)) -> EntryOut:
    repo = EntriesRepo(db)
    try:
        return _to_out(repo.get(entry_id))
    except NoResultFound:
        raise HTTPException(status_code=404, detail="entry not found")


@router.put("/{entry_id}")
def update_entry(entry_id: str, payload: EntryUpdateIn, db: Session = Depends(db_session)) -> EntryOut:
    repo = EntriesRepo(db)
    try:
        return _to_out(repo.update(entry_id, data=payload.data, tags=payload.tags))
    except NoResultFound:
        raise HTTPException(status_code=404, detail="entry not found")


@router.delete("/{entry_id}")
def delete_entry(entry_id: str, db: Session = Depends(db_session)) -> dict[str, str]:
    repo = EntriesRepo(db)
    repo.delete(entry_id)
    return {"status": "ok"}


