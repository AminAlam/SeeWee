from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from core.document_model import DocItem, DocSection, Document
from core.repos.entries_repo import EntriesRepo
from core.repos.variants_repo import VariantsRepo


def _title_for_section(section_id: str) -> str:
    # MVP: keep titles simple; exporters can later map to display names.
    return section_id.replace("_", " ").title()


def _matches_rules(*, tags: list[str], rules: dict[str, Any]) -> bool:
    include_tags = rules.get("include_tags") or []
    exclude_tags = rules.get("exclude_tags") or []

    tag_set = set(tags)

    if include_tags:
        if not (tag_set & set(include_tags)):
            return False

    if exclude_tags:
        if tag_set & set(exclude_tags):
            return False

    return True


def _build_from_layout(
    variant_id: str,
    layout_sections: dict[str, list[str]],
    entries_by_id: dict[str, Any],
) -> Document:
    """Build document from a manual layout."""
    sections: list[DocSection] = []
    for section_id, entry_ids in layout_sections.items():
        items: list[DocItem] = []
        for eid in entry_ids:
            entry = entries_by_id.get(eid)
            if entry:
                items.append(
                    DocItem(
                        entry_id=entry.id,
                        entry_type=entry.type,
                        data=entry.data,
                        tags=entry.tags,
                    )
                )
        sections.append(DocSection(id=section_id, title=_title_for_section(section_id), items=items))
    return Document(variant_id=variant_id, generated_at=datetime.now(timezone.utc), sections=sections)


def _build_auto_grouped(
    variant_id: str,
    section_ids: list[str],
    all_entries: list[Any],
    rules: dict[str, Any],
) -> Document:
    """Build document by auto-grouping entries into sections by type."""
    section_to_entry_types: dict[str, set[str]] = {
        "experience": {"experience"},
        "education": {"education"},
        "projects": {"project", "projects"},
        "publications": {"publication", "publications"},
        "awards": {"award", "awards", "honor", "honors"},
        "volunteering": {"volunteering", "volunteer"},
        "skills": {"skill", "skills"},
        "teaching": {"teaching"},
        "certifications": {"certification", "certifications"},
        "languages": {"language", "languages"},
        "talks": {"talk", "talks"},
        "interests": {"interest", "interests"},
        "references": {"reference", "references"},
    }

    by_section: dict[str, list[DocItem]] = {sid: [] for sid in section_ids}
    for e in all_entries:
        if not _matches_rules(tags=e.tags, rules=rules):
            continue
        for sid in section_ids:
            allowed = section_to_entry_types.get(sid, {sid})
            if e.type in allowed:
                by_section.setdefault(sid, []).append(
                    DocItem(entry_id=e.id, entry_type=e.type, data=e.data, tags=e.tags)
                )
                break

    sections: list[DocSection] = []
    for sid in section_ids:
        sections.append(DocSection(id=sid, title=_title_for_section(sid), items=by_section.get(sid, [])))

    return Document(variant_id=variant_id, generated_at=datetime.now(timezone.utc), sections=sections)


def build_variant_preview(db: Session, variant_id: str) -> dict[str, Any]:
    """
    Build a normalized document model for a variant.

    If the variant has a manual layout, use that exact ordering.
    Otherwise, auto-group entries by type into sections.

    MVP rules supported (for auto-grouping):
    - rules.include_tags: entry must contain at least one (OR) tag if provided
    - rules.exclude_tags: entry must contain none
    """
    variants_repo = VariantsRepo(db)
    entries_repo = EntriesRepo(db)

    try:
        variant = variants_repo.get(variant_id)
    except NoResultFound:
        raise

    all_entries = entries_repo.list()
    entries_by_id = {e.id: e for e in all_entries}

    # If variant has a manual layout, use it
    if variant.layout and variant.layout.sections:
        doc = _build_from_layout(variant_id, variant.layout.sections, entries_by_id)
        return asdict(doc)

    # Otherwise, fall back to auto-grouping
    section_ids = [s for (s, _pos) in variant.sections] if variant.sections else []
    if not section_ids:
        # fallback: include all known types if variant has no explicit sections yet
        section_ids = [
            "experience",
            "education",
            "projects",
            "publications",
            "awards",
            "volunteering",
            "skills",
            "teaching",
            "certifications",
            "languages",
            "talks",
            "interests",
            "references",
        ]

    doc = _build_auto_grouped(variant_id, section_ids, all_entries, variant.rules)
    return asdict(doc)


def build_variant_document(db: Session, variant_id: str) -> Document:
    """
    Same as `build_variant_preview`, but returns the strongly-typed document.
    """
    preview = build_variant_preview(db, variant_id)
    sections: list[DocSection] = []
    for s in preview["sections"]:
        items = [
            DocItem(
                entry_id=i["entry_id"],
                entry_type=i["entry_type"],
                data=i["data"],
                tags=i["tags"],
            )
            for i in s["items"]
        ]
        sections.append(DocSection(id=s["id"], title=s["title"], items=items))
    ga = preview["generated_at"]
    generated_at = datetime.fromisoformat(ga) if isinstance(ga, str) else ga
    return Document(variant_id=preview["variant_id"], generated_at=generated_at, sections=sections)


