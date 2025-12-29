from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.db import db_session
from core.repos.profile_repo import ProfileRepo

router = APIRouter(prefix="/profile", tags=["profile"])


class ProfileOut(BaseModel):
    data: dict[str, Any]
    created_at: str
    updated_at: str


class ProfilePutIn(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)


@router.get("")
def get_profile(db: Session = Depends(db_session)) -> ProfileOut:
    r = ProfileRepo(db).get()
    return ProfileOut(data=r.data, created_at=r.created_at.isoformat(), updated_at=r.updated_at.isoformat())


@router.put("")
def put_profile(payload: ProfilePutIn, db: Session = Depends(db_session)) -> ProfileOut:
    r = ProfileRepo(db).put(payload.data)
    return ProfileOut(data=r.data, created_at=r.created_at.isoformat(), updated_at=r.updated_at.isoformat())



