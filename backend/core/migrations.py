from __future__ import annotations

import os
from pathlib import Path

from alembic import command
from alembic.config import Config


def upgrade_to_head() -> None:
    """
    Run Alembic migrations up to head.

    This is used at API startup so a fresh install works via `docker compose up`.
    """
    backend_dir = Path(__file__).resolve().parents[1]
    alembic_ini = backend_dir / "alembic.ini"
    if not alembic_ini.exists():
        raise RuntimeError(f"Missing alembic.ini at {alembic_ini}")

    cfg = Config(str(alembic_ini))

    # Ensure Alembic can import `core.*` via `prepend_sys_path = .` in alembic.ini
    cfg.set_main_option("script_location", "migrations")

    # Respect SEEWEE_DB_PATH (used by migrations/env.py)
    os.environ.setdefault("SEEWEE_DB_PATH", "/data/seewee.db")

    command.upgrade(cfg, "head")


