from __future__ import annotations

import csv
import json
from io import StringIO
from typing import Any

from core.document_model import Document, DocItem
from core.markdown_utils import md_to_plain


def _as_str(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    return str(v)


def _join_bullets(item: DocItem) -> str:
    """Join bullet points, converting any markdown to plain text."""
    data = item.data or {}
    highlights = data.get("highlights")
    if isinstance(highlights, list):
        # Convert each bullet from markdown to plain text
        bullets = [md_to_plain(_as_str(x)).strip() for x in highlights if _as_str(x).strip()]
        return "\n".join(f"- {b}" for b in bullets)
    return ""


def _field(data: dict[str, Any], *keys: str) -> str:
    for k in keys:
        v = data.get(k)
        if v is not None and _as_str(v).strip():
            return _as_str(v).strip()
    return ""


def render_linkedin_bundle(doc: Document) -> dict[str, str]:
    """
    Export a LinkedIn-friendly bundle for manual entry (copy/paste or CSV).
    """
    rows: list[dict[str, str]] = []
    copy_blocks: list[str] = []

    for section in doc.sections:
        for item in section.items:
            d = item.data or {}
            title = _field(d, "title", "role", "position", "name") or item.entry_type
            company = _field(d, "company", "org", "organization")
            location = _field(d, "location")
            start_date = _field(d, "start_date", "start")
            end_date = _field(d, "end_date", "end")
            description = _join_bullets(item)

            rows.append(
                {
                    "entry_type": item.entry_type,
                    "title": title,
                    "company": company,
                    "location": location,
                    "start_date": start_date,
                    "end_date": end_date,
                    "description": description,
                    "tags": ",".join(item.tags or []),
                }
            )

            header = " — ".join([p for p in [title, company] if p])
            copy_blocks.append(header)
            if location:
                copy_blocks.append(f"Location: {location}")
            if start_date or end_date:
                copy_blocks.append(f"Dates: {start_date} - {end_date}".strip())
            if description:
                copy_blocks.append(description)
            copy_blocks.append("")  # spacer

    sio = StringIO()
    writer = csv.DictWriter(
        sio,
        fieldnames=["entry_type", "title", "company", "location", "start_date", "end_date", "description", "tags"],
    )
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

    mapping_json = json.dumps(
        {"variant_id": doc.variant_id, "generated_at": doc.generated_at.isoformat(), "rows": rows},
        ensure_ascii=False,
        indent=2,
    )

    checklist = """SeeWee LinkedIn-friendly export (manual)\n\nSuggested flow:\n1) Open LinkedIn profile edit\n2) For each row in linkedin_experience.csv:\n   - Copy title/company/location/dates\n   - Paste bullet list into Description\n3) Optional: keep copy_blocks.txt open for quick copy/paste\n\nNotes:\n- This is NOT automated form-filling.\n- Field names are best-effort based on your entry JSON keys.\n"""

    return {
        "linkedin_experience.csv": sio.getvalue(),
        "copy_blocks.txt": "\n".join(copy_blocks).strip() + "\n",
        "mapping.json": mapping_json + "\n",
        "README.txt": checklist,
    }


