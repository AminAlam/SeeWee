from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from api.settings import settings
from core.db import create_session_factory, create_sqlite_engine

_engine = create_sqlite_engine(settings.db_path)
_session_factory: sessionmaker[Session] = create_session_factory(_engine)

def db_session() -> Generator[Session, None, None]:
    session = _session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


