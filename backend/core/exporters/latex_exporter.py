from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from core.document_model import Document, DocSection
from core.entry_schemas import normalize_entry


def _tex_escape(s: str) -> str:
    # Minimal escaping for common LaTeX special chars.
    mapping = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(mapping.get(ch, ch) for ch in s)


def _as_str(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    return str(v)


def _bullets_from_data(data: dict[str, Any]) -> list[str]:
    highlights = data.get("highlights")
    if isinstance(highlights, list):
        return [_as_str(x) for x in highlights if _as_str(x).strip()]
    return []


def _title_line(entry_type: str, data: dict[str, Any]) -> str:
    title = _as_str(data.get("title") or data.get("role") or data.get("name") or "")
    org = _as_str(data.get("org") or data.get("organization") or "")
    dates = _as_str(data.get("dates") or "")
    parts = [p for p in [title, org, dates] if p]
    if not parts:
        parts = [entry_type]
    return " --- ".join(parts)


def render_latex(doc: Document) -> str:
    raise RuntimeError("Use render_latex_template(...) in this project")


def _section_title_for_variant_section(section_id: str) -> str:
    mapping = {
        "experience": "Professional Experience",
        "education": "Education",
        "projects": "Projects",
        "publications": "Selected Publications",
        "awards": "Key Achievements & Awards",
        "volunteering": "Volunteering & Open Source Contributions",
        "skills": "Technical Skills",
        "teaching": "Teaching Experience",
        "certifications": "Certifications",
        "languages": "Languages",
        "talks": "Talks & Presentations",
        "interests": "Interests",
        "references": "References",
    }
    return mapping.get(section_id, section_id.replace("_", " ").title())


def _normalize_section(section: DocSection) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for it in section.items:
        # Use the schema-based normalization
        normalized = normalize_entry(it.entry_type, it.data or {})

        # Build common fields for backward compatibility
        header = _as_str(
            normalized.get("role") or normalized.get("title") or normalized.get("name") or
            normalized.get("degree") or normalized.get("category") or it.entry_type
        )
        org = _as_str(
            normalized.get("company") or normalized.get("organization") or
            normalized.get("school") or normalized.get("issuer") or normalized.get("venue") or ""
        )
        location = _as_str(normalized.get("location") or "")
        subheader = ", ".join([p for p in [org, location] if p])

        # Dates - use computed _dates or build from start/end
        dates = _as_str(normalized.get("_dates") or normalized.get("date") or normalized.get("year") or "")

        # Bullets/highlights
        bullets = normalized.get("highlights") or []
        if not bullets and normalized.get("skill_list"):
            bullets = normalized.get("skill_list", [])

        items.append({
            # Common fields
            "header": header,
            "subheader": subheader,
            "dates": dates,
            "bullets": bullets,
            "type": it.entry_type,
            # Type-specific fields (all normalized)
            **normalized,
        })
    return {"id": section.id, "title": _section_title_for_variant_section(section.id), "entries": items, "type": section.id}


def render_latex_template(doc: Document, profile: dict[str, Any]) -> str:
    backend_dir = Path(__file__).resolve().parents[1]
    templates_dir = backend_dir / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["tex_escape"] = _tex_escape

    tpl = env.get_template("cv_template.tex.j2")

    links = (profile or {}).get("links") or {}
    personal = (profile or {}).get("personal") or {}
    content = (profile or {}).get("content") or {}

    ctx = {
        "full_name": personal.get("full_name", "Your Name"),
        "email": links.get("email", ""),
        "phone": links.get("phone", ""),
        "address": links.get("address", ""),
        "github": links.get("github", ""),
        "linkedin": links.get("linkedin", ""),
        "summary": content.get("summary", ""),
        "sections": [_normalize_section(s) for s in doc.sections if s.items],
    }
    return tpl.render(**ctx)


