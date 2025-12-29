from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.db import db_session
from core.repos.tags_repo import TagsRepo

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("")
def list_tags(db: Session = Depends(db_session)) -> list[str]:
    return TagsRepo(db).list()



