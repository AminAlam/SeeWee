from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models import EntryTag


class TagsRepo:
    def __init__(self, session: Session):
        self._session = session

    def list(self) -> list[str]:
        rows = self._session.execute(select(EntryTag.tag).distinct().order_by(EntryTag.tag.asc())).scalars().all()
        return list(rows)


