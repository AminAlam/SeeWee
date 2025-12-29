from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def sqlite_url(db_path: str) -> str:
    return f"sqlite+pysqlite:///{db_path}"


def create_sqlite_engine(db_path: str) -> Engine:
    return create_engine(
        sqlite_url(db_path),
        connect_args={"check_same_thread": False},
        future=True,
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def session_scope(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()



