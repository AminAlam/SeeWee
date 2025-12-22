from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from core.models import Entry, EntryTag, utcnow


@dataclass(frozen=True)
class EntryRecord:
    id: str
    type: str
    data: dict
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class EntriesRepo:
    def __init__(self, session: Session):
        self._session = session

    def create(self, *, entry_type: str, data: dict, tags: list[str] | None = None) -> EntryRecord:
        entry_id = str(uuid4())
        now = utcnow()

        row = Entry(
            id=entry_id,
            type=entry_type,
            data_json=json.dumps(data, ensure_ascii=False),
            created_at=now,
            updated_at=now,
        )
        self._session.add(row)

        for t in tags or []:
            self._session.add(EntryTag(entry_id=entry_id, tag=t))

        self._session.flush()
        return self.get(entry_id)

    def get(self, entry_id: str) -> EntryRecord:
        entry = self._session.execute(select(Entry).where(Entry.id == entry_id)).scalar_one()
        tags = self._session.execute(select(EntryTag.tag).where(EntryTag.entry_id == entry_id)).scalars().all()
        return EntryRecord(
            id=entry.id,
            type=entry.type,
            data=json.loads(entry.data_json),
            tags=list(tags),
            created_at=entry.created_at,
            updated_at=entry.updated_at,
        )

    def list(self, *, entry_type: str | None = None) -> list[EntryRecord]:
        stmt = select(Entry)
        if entry_type:
            stmt = stmt.where(Entry.type == entry_type)
        stmt = stmt.order_by(Entry.updated_at.desc())

        entries = self._session.execute(stmt).scalars().all()
        out: list[EntryRecord] = []
        for e in entries:
            tags = (
                self._session.execute(select(EntryTag.tag).where(EntryTag.entry_id == e.id)).scalars().all()
            )
            out.append(
                EntryRecord(
                    id=e.id,
                    type=e.type,
                    data=json.loads(e.data_json),
                    tags=list(tags),
                    created_at=e.created_at,
                    updated_at=e.updated_at,
                )
            )
        return out

    def update(self, entry_id: str, *, data: dict | None = None, tags: list[str] | None = None) -> EntryRecord:
        if data is not None:
            self._session.execute(
                update(Entry)
                .where(Entry.id == entry_id)
                .values(data_json=json.dumps(data, ensure_ascii=False), updated_at=utcnow())
            )

        if tags is not None:
            self._session.execute(delete(EntryTag).where(EntryTag.entry_id == entry_id))
            for t in tags:
                self._session.add(EntryTag(entry_id=entry_id, tag=t))

        self._session.flush()
        return self.get(entry_id)

    def delete(self, entry_id: str) -> None:
        self._session.execute(delete(Entry).where(Entry.id == entry_id))
        self._session.flush()


