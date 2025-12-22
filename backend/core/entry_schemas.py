"""
Typed entry schema registry.

Each entry type has:
- A Pydantic model for validation
- A normalization function (map legacy/variant JSON to the canonical schema)
- An export model function (produce a consistent render context for LaTeX/HTML)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal

from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Entry type definitions
# -----------------------------------------------------------------------------

ENTRY_TYPES = [
    "experience",
    "education",
    "project",
    "publication",
    "skill",
    "award",
    "volunteering",
    "certification",
    "talk",
    "language",
    "reference",
]


# -----------------------------------------------------------------------------
# Schema models (Pydantic) for each entry type
# -----------------------------------------------------------------------------


class ExperienceSchema(BaseModel):
    """Work experience / professional role."""

    role: str = Field(default="", description="Job title or role")
    company: str = Field(default="", description="Company or organization name")
    location: str = Field(default="", description="City, Country")
    start_date: str = Field(default="", description="Start date (e.g. 'March 2024')")
    end_date: str = Field(default="", description="End date or 'Present'")
    lead: str = Field(default="", description="Optional leadership title (e.g. 'Engineering Lead')")
    highlights: list[str] = Field(default_factory=list, description="Bullet point achievements")


class EducationSchema(BaseModel):
    """Educational background."""

    school: str = Field(default="", description="University or institution name")
    degree: str = Field(default="", description="Degree name (e.g. 'BSc Computer Science')")
    location: str = Field(default="", description="City, Country")
    start_date: str = Field(default="", description="Start year/date")
    end_date: str = Field(default="", description="End year/date or 'Expected 2025'")
    gpa: str = Field(default="", description="GPA (e.g. '3.9/4.0')")
    honors: str = Field(default="", description="Honors, distinctions, or additional notes")
    highlights: list[str] = Field(default_factory=list, description="Optional bullet points")


class ProjectSchema(BaseModel):
    """Personal or professional project."""

    name: str = Field(default="", description="Project name")
    organization: str = Field(default="", description="Associated org/company (optional)")
    link: str = Field(default="", description="URL to project")
    tech_stack: list[str] = Field(default_factory=list, description="Technologies used")
    start_date: str = Field(default="", description="Start date")
    end_date: str = Field(default="", description="End date or 'Ongoing'")
    highlights: list[str] = Field(default_factory=list, description="Bullet point descriptions")


class PublicationSchema(BaseModel):
    """Academic publication."""

    title: str = Field(default="", description="Publication title")
    authors: str = Field(default="", description="Author list (formatted string)")
    venue: str = Field(default="", description="Journal, conference, or arXiv")
    year: str = Field(default="", description="Publication year")
    doi: str = Field(default="", description="DOI or URL")
    link: str = Field(default="", description="Direct link (if different from DOI)")
    highlights: list[str] = Field(default_factory=list, description="Optional notes")


class SkillSchema(BaseModel):
    """Skill category with items."""

    category: str = Field(default="", description="Category name (e.g. 'Programming Languages')")
    skill_list: list[str] = Field(default_factory=list, description="List of skills in this category")
    # Alternative: single skill with level
    name: str = Field(default="", description="Single skill name (alternative to category)")
    level: str = Field(default="", description="Proficiency level (e.g. 'Expert', 'Intermediate')")


class AwardSchema(BaseModel):
    """Award, honor, or achievement."""

    title: str = Field(default="", description="Award name")
    issuer: str = Field(default="", description="Granting organization")
    date: str = Field(default="", description="Date or year received")
    description: str = Field(default="", description="Details about the award")
    highlights: list[str] = Field(default_factory=list, description="Bullet points")


class VolunteeringSchema(BaseModel):
    """Volunteering, open source, or extracurricular."""

    role: str = Field(default="", description="Role or title")
    organization: str = Field(default="", description="Organization name")
    location: str = Field(default="", description="Location (optional)")
    start_date: str = Field(default="", description="Start date")
    end_date: str = Field(default="", description="End date")
    link: str = Field(default="", description="Link to project/org")
    highlights: list[str] = Field(default_factory=list, description="Bullet point descriptions")


class CertificationSchema(BaseModel):
    """Professional certification."""

    name: str = Field(default="", description="Certification name")
    issuer: str = Field(default="", description="Issuing organization")
    date: str = Field(default="", description="Date obtained")
    expiry: str = Field(default="", description="Expiration date (if applicable)")
    credential_id: str = Field(default="", description="Credential ID")
    link: str = Field(default="", description="Verification URL")


class TalkSchema(BaseModel):
    """Talk, presentation, or lecture."""

    title: str = Field(default="", description="Talk title")
    event: str = Field(default="", description="Event or conference name")
    location: str = Field(default="", description="Location")
    date: str = Field(default="", description="Date of presentation")
    link: str = Field(default="", description="Link to slides/recording")
    highlights: list[str] = Field(default_factory=list, description="Optional notes")


class LanguageSchema(BaseModel):
    """Language proficiency."""

    name: str = Field(default="", description="Language name")
    proficiency: str = Field(default="", description="Proficiency level (e.g. 'Native', 'Fluent', 'Basic')")


class ReferenceSchema(BaseModel):
    """Professional reference."""

    name: str = Field(default="", description="Reference's full name")
    title: str = Field(default="", description="Job title")
    organization: str = Field(default="", description="Organization")
    email: str = Field(default="", description="Contact email")
    phone: str = Field(default="", description="Contact phone")
    relationship: str = Field(default="", description="Relationship to you")


# -----------------------------------------------------------------------------
# Schema registry
# -----------------------------------------------------------------------------

SCHEMA_REGISTRY: dict[str, type[BaseModel]] = {
    "experience": ExperienceSchema,
    "education": EducationSchema,
    "project": ProjectSchema,
    "publication": PublicationSchema,
    "skill": SkillSchema,
    "award": AwardSchema,
    "volunteering": VolunteeringSchema,
    "certification": CertificationSchema,
    "talk": TalkSchema,
    "language": LanguageSchema,
    "reference": ReferenceSchema,
}


# -----------------------------------------------------------------------------
# Normalization functions (legacy JSON -> canonical schema)
# -----------------------------------------------------------------------------


def _get_str(data: dict[str, Any], *keys: str, default: str = "") -> str:
    """Get first matching key as string."""
    for key in keys:
        val = data.get(key)
        if val is not None:
            return str(val) if not isinstance(val, str) else val
    return default


def _get_list(data: dict[str, Any], *keys: str) -> list[str]:
    """Get first matching key as list of strings."""
    for key in keys:
        val = data.get(key)
        if isinstance(val, list):
            return [str(x) for x in val if x]
        if isinstance(val, str) and val.strip():
            # Could be comma-separated
            return [v.strip() for v in val.split(",") if v.strip()]
    return []


def _build_dates(data: dict[str, Any]) -> str:
    """Build a dates string from start/end fields."""
    start = _get_str(data, "start_date", "start", "from")
    end = _get_str(data, "end_date", "end", "to")
    if start and end:
        return f"{start} - {end}"
    if start:
        return f"{start} - Present"
    if end:
        return end
    return _get_str(data, "dates", "date", "year")


def normalize_experience(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "role": _get_str(data, "role", "title", "position", "header"),
        "company": _get_str(data, "company", "org", "organization", "employer"),
        "location": _get_str(data, "location", "place"),
        "start_date": _get_str(data, "start_date", "start", "from"),
        "end_date": _get_str(data, "end_date", "end", "to"),
        "lead": _get_str(data, "lead", "leadership", "secondary_title"),
        "highlights": _get_list(data, "highlights", "bullets", "description"),
        # Computed for rendering
        "_dates": _build_dates(data),
    }


def normalize_education(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "school": _get_str(data, "school", "institution", "university", "org", "organization", "subheader"),
        "degree": _get_str(data, "degree", "title", "program", "header"),
        "location": _get_str(data, "location", "place"),
        "start_date": _get_str(data, "start_date", "start", "from"),
        "end_date": _get_str(data, "end_date", "end", "to"),
        "gpa": _get_str(data, "gpa", "grade", "score"),
        "honors": _get_str(data, "honors", "distinction", "notes"),
        "highlights": _get_list(data, "highlights", "bullets"),
        "_dates": _build_dates(data),
    }


def normalize_project(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": _get_str(data, "name", "title", "project_name", "header"),
        "organization": _get_str(data, "organization", "org", "company", "affiliation"),
        "link": _get_str(data, "link", "url", "repo", "github"),
        "tech_stack": _get_list(data, "tech_stack", "technologies", "stack", "tech"),
        "start_date": _get_str(data, "start_date", "start"),
        "end_date": _get_str(data, "end_date", "end"),
        "highlights": _get_list(data, "highlights", "bullets", "description"),
        "_dates": _build_dates(data),
    }


def normalize_publication(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": _get_str(data, "title", "name", "header"),
        "authors": _get_str(data, "authors", "author", "by"),
        "venue": _get_str(data, "venue", "journal", "conference", "publication", "subheader"),
        "year": _get_str(data, "year", "date", "published"),
        "doi": _get_str(data, "doi"),
        "link": _get_str(data, "link", "url"),
        "highlights": _get_list(data, "highlights", "notes"),
    }


def normalize_skill(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "category": _get_str(data, "category", "group", "header", "title"),
        "skill_list": _get_list(data, "skill_list", "items", "skills", "list", "bullets"),
        "name": _get_str(data, "name", "skill"),
        "level": _get_str(data, "level", "proficiency"),
    }


def normalize_award(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": _get_str(data, "title", "name", "award", "header"),
        "issuer": _get_str(data, "issuer", "organization", "org", "from", "grantor"),
        "date": _get_str(data, "date", "year", "received"),
        "description": _get_str(data, "description", "details", "notes"),
        "highlights": _get_list(data, "highlights", "bullets"),
    }


def normalize_volunteering(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "role": _get_str(data, "role", "title", "position", "header"),
        "organization": _get_str(data, "organization", "org", "company", "subheader"),
        "location": _get_str(data, "location", "place"),
        "start_date": _get_str(data, "start_date", "start"),
        "end_date": _get_str(data, "end_date", "end"),
        "link": _get_str(data, "link", "url"),
        "highlights": _get_list(data, "highlights", "bullets", "description"),
        "_dates": _build_dates(data),
    }


def normalize_certification(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": _get_str(data, "name", "title", "certification", "header"),
        "issuer": _get_str(data, "issuer", "organization", "org", "from"),
        "date": _get_str(data, "date", "issued", "received"),
        "expiry": _get_str(data, "expiry", "expires", "valid_until"),
        "credential_id": _get_str(data, "credential_id", "id", "credential"),
        "link": _get_str(data, "link", "url", "verify"),
    }


def normalize_talk(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": _get_str(data, "title", "name", "talk", "header"),
        "event": _get_str(data, "event", "conference", "venue", "subheader"),
        "location": _get_str(data, "location", "place"),
        "date": _get_str(data, "date", "year", "presented"),
        "link": _get_str(data, "link", "url", "slides"),
        "highlights": _get_list(data, "highlights", "notes"),
    }


def normalize_language(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": _get_str(data, "name", "language", "lang", "header"),
        "proficiency": _get_str(data, "proficiency", "level", "fluency"),
    }


def normalize_reference(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": _get_str(data, "name", "full_name", "header"),
        "title": _get_str(data, "title", "position", "role"),
        "organization": _get_str(data, "organization", "org", "company"),
        "email": _get_str(data, "email", "contact_email"),
        "phone": _get_str(data, "phone", "contact_phone"),
        "relationship": _get_str(data, "relationship", "relation"),
    }


NORMALIZERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "experience": normalize_experience,
    "education": normalize_education,
    "project": normalize_project,
    "publication": normalize_publication,
    "skill": normalize_skill,
    "award": normalize_award,
    "volunteering": normalize_volunteering,
    "certification": normalize_certification,
    "talk": normalize_talk,
    "language": normalize_language,
    "reference": normalize_reference,
}


def normalize_entry(entry_type: str, data: dict[str, Any]) -> dict[str, Any]:
    """Normalize entry data to canonical schema format."""
    normalizer = NORMALIZERS.get(entry_type)
    if normalizer:
        return normalizer(data)
    # Fallback: return data as-is with some common field mapping
    return {
        "title": _get_str(data, "title", "name", "header"),
        "organization": _get_str(data, "organization", "org", "company", "subheader"),
        "dates": _build_dates(data),
        "highlights": _get_list(data, "highlights", "bullets"),
        **data,
    }


# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------


def validate_entry(entry_type: str, data: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate entry data against its schema.
    Returns (is_valid, list_of_errors).
    """
    schema_cls = SCHEMA_REGISTRY.get(entry_type)
    if not schema_cls:
        # Unknown type, accept any data
        return True, []

    try:
        schema_cls.model_validate(data)
        return True, []
    except Exception as e:
        return False, [str(e)]


def get_default_data(entry_type: str) -> dict[str, Any]:
    """Get default/empty data for an entry type."""
    schema_cls = SCHEMA_REGISTRY.get(entry_type)
    if schema_cls:
        return schema_cls().model_dump()
    return {}


# -----------------------------------------------------------------------------
# Schema metadata for UI
# -----------------------------------------------------------------------------


@dataclass
class FieldMeta:
    name: str
    label: str
    field_type: Literal["text", "textarea", "list", "date"]
    description: str = ""
    required: bool = False


def get_schema_fields(entry_type: str) -> list[FieldMeta]:
    """Get field metadata for UI form generation."""
    schema_cls = SCHEMA_REGISTRY.get(entry_type)
    if not schema_cls:
        return []

    fields: list[FieldMeta] = []
    for name, field_info in schema_cls.model_fields.items():
        annotation = field_info.annotation
        description = field_info.description or ""

        # Determine field type
        if annotation == list[str]:
            field_type: Literal["text", "textarea", "list", "date"] = "list"
        elif "date" in name.lower():
            field_type = "date"
        elif name in ("description", "highlights"):
            field_type = "textarea"
        else:
            field_type = "text"

        # Nice label
        label = name.replace("_", " ").title()

        fields.append(
            FieldMeta(
                name=name,
                label=label,
                field_type=field_type,
                description=description,
                required=field_info.is_required(),
            )
        )

    return fields


def get_all_schemas_for_ui() -> dict[str, Any]:
    """Get all schemas with field metadata for the frontend."""
    result = {}
    for entry_type in ENTRY_TYPES:
        fields = get_schema_fields(entry_type)
        result[entry_type] = {
            "type": entry_type,
            "label": entry_type.replace("_", " ").title(),
            "fields": [
                {
                    "name": f.name,
                    "label": f.label,
                    "type": f.field_type,
                    "description": f.description,
                    "required": f.required,
                }
                for f in fields
            ],
            "default": get_default_data(entry_type),
        }
    return result

