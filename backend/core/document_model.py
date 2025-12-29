from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class DocItem:
    entry_id: str
    entry_type: str
    data: dict[str, Any]
    tags: list[str]


@dataclass(frozen=True)
class DocSection:
    id: str
    title: str
    items: list[DocItem]


@dataclass(frozen=True)
class Document:
    variant_id: str
    generated_at: datetime
    sections: list[DocSection]



