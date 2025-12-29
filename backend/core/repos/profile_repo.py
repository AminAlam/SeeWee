from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models import Profile, utcnow


@dataclass(frozen=True)
class ProfileRecord:
    data: dict
    created_at: datetime
    updated_at: datetime


class ProfileRepo:
    def __init__(self, session: Session):
        self._session = session

    def get(self) -> ProfileRecord:
        row = self._session.execute(select(Profile).where(Profile.id == 1)).scalar_one_or_none()
        if row is None:
            now = utcnow()
            row = Profile(id=1, data_json=json.dumps({}, ensure_ascii=False), created_at=now, updated_at=now)
            self._session.add(row)
            self._session.flush()
        return ProfileRecord(data=json.loads(row.data_json), created_at=row.created_at, updated_at=row.updated_at)

    def put(self, data: dict) -> ProfileRecord:
        row = self._session.execute(select(Profile).where(Profile.id == 1)).scalar_one_or_none()
        now = utcnow()
        if row is None:
            row = Profile(id=1, data_json=json.dumps(data, ensure_ascii=False), created_at=now, updated_at=now)
            self._session.add(row)
        else:
            row.data_json = json.dumps(data, ensure_ascii=False)
            row.updated_at = now
        self._session.flush()
        return self.get()



