from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from core.models import Variant, VariantSection, VariantItem, utcnow


@dataclass(frozen=True)
class VariantLayoutItem:
    """One entry placed in a section."""
    entry_id: str
    position: int


@dataclass(frozen=True)
class VariantLayout:
    """Full layout of a variant: which entries are in which sections, in order."""
    sections: dict[str, list[str]]  # section_id -> list of entry_ids in order


@dataclass(frozen=True)
class VariantRecord:
    id: str
    name: str
    rules: dict
    sections: list[tuple[str, int]]
    created_at: datetime
    updated_at: datetime
    layout: VariantLayout | None = None


class VariantsRepo:
    def __init__(self, session: Session):
        self._session = session

    def create(self, *, name: str, rules: dict, sections: list[str] | None = None) -> VariantRecord:
        variant_id = str(uuid4())
        now = utcnow()
        row = Variant(
            id=variant_id,
            name=name,
            rules_json=json.dumps(rules, ensure_ascii=False),
            created_at=now,
            updated_at=now,
        )
        self._session.add(row)

        if sections:
            for idx, section in enumerate(sections):
                self._session.add(VariantSection(variant_id=variant_id, section=section, position=idx))

        self._session.flush()
        return self.get(variant_id)

    def _load_layout(self, variant_id: str) -> VariantLayout | None:
        """Load the manual layout for a variant, if any."""
        items = (
            self._session.execute(
                select(VariantItem.section, VariantItem.entry_id, VariantItem.position)
                .where(VariantItem.variant_id == variant_id)
                .order_by(VariantItem.section, VariantItem.position)
            )
            .all()
        )
        if not items:
            return None

        sections: dict[str, list[str]] = {}
        for section, entry_id, _pos in items:
            if section not in sections:
                sections[section] = []
            sections[section].append(entry_id)
        return VariantLayout(sections=sections)

    def get(self, variant_id: str) -> VariantRecord:
        v = self._session.execute(select(Variant).where(Variant.id == variant_id)).scalar_one()
        sections = (
            self._session.execute(
                select(VariantSection.section, VariantSection.position)
                .where(VariantSection.variant_id == variant_id)
                .order_by(VariantSection.position.asc())
            )
            .all()
        )
        layout = self._load_layout(variant_id)
        return VariantRecord(
            id=v.id,
            name=v.name,
            rules=json.loads(v.rules_json),
            sections=[(s, p) for (s, p) in sections],
            created_at=v.created_at,
            updated_at=v.updated_at,
            layout=layout,
        )

    def list(self) -> list[VariantRecord]:
        variants = self._session.execute(select(Variant).order_by(Variant.updated_at.desc())).scalars().all()
        return [self.get(v.id) for v in variants]

    def update(
        self,
        variant_id: str,
        *,
        name: str | None = None,
        rules: dict | None = None,
        sections: list[str] | None = None,
    ) -> VariantRecord:
        patch: dict = {"updated_at": utcnow()}
        if name is not None:
            patch["name"] = name
        if rules is not None:
            patch["rules_json"] = json.dumps(rules, ensure_ascii=False)
        if len(patch) > 1:
            self._session.execute(update(Variant).where(Variant.id == variant_id).values(**patch))

        if sections is not None:
            self._session.execute(delete(VariantSection).where(VariantSection.variant_id == variant_id))
            for idx, section in enumerate(sections):
                self._session.add(VariantSection(variant_id=variant_id, section=section, position=idx))

        self._session.flush()
        return self.get(variant_id)

    def delete(self, variant_id: str) -> None:
        self._session.execute(delete(Variant).where(Variant.id == variant_id))
        self._session.flush()

    def get_layout(self, variant_id: str) -> VariantLayout | None:
        """Get the manual layout for a variant."""
        return self._load_layout(variant_id)

    def set_layout(self, variant_id: str, layout: dict[str, list[str]]) -> VariantLayout:
        """
        Set the manual layout for a variant.
        layout: { section_id: [entry_id, entry_id, ...], ... }
        """
        # Clear existing layout
        self._session.execute(delete(VariantItem).where(VariantItem.variant_id == variant_id))

        # Insert new layout
        for section, entry_ids in layout.items():
            for position, entry_id in enumerate(entry_ids):
                self._session.add(
                    VariantItem(
                        variant_id=variant_id,
                        section=section,
                        position=position,
                        entry_id=entry_id,
                    )
                )

        # Also update sections order based on layout keys
        self._session.execute(delete(VariantSection).where(VariantSection.variant_id == variant_id))
        for idx, section in enumerate(layout.keys()):
            self._session.add(VariantSection(variant_id=variant_id, section=section, position=idx))

        # Update variant timestamp
        self._session.execute(
            update(Variant).where(Variant.id == variant_id).values(updated_at=utcnow())
        )

        self._session.flush()
        return VariantLayout(sections=layout)

    def clear_layout(self, variant_id: str) -> None:
        """Clear the manual layout for a variant (revert to auto-grouping)."""
        self._session.execute(delete(VariantItem).where(VariantItem.variant_id == variant_id))
        self._session.execute(
            update(Variant).where(Variant.id == variant_id).values(updated_at=utcnow())
        )
        self._session.flush()


