"""
Unit tests for entry schemas and normalization.
"""

import pytest
from core.entry_schemas import (
    ENTRY_TYPES,
    SCHEMA_REGISTRY,
    normalize_entry,
    normalize_experience,
    normalize_education,
    normalize_skill,
    normalize_project,
    normalize_publication,
    normalize_award,
    validate_entry,
    get_default_data,
    get_all_schemas_for_ui,
)


class TestEntryTypes:
    """Test entry type definitions."""

    def test_entry_types_defined(self):
        """All expected entry types should be defined."""
        expected = [
            "experience", "education", "project", "publication",
            "skill", "award", "volunteering", "certification",
            "talk", "language", "reference"
        ]
        for t in expected:
            assert t in ENTRY_TYPES

    def test_schema_registry_complete(self):
        """Each entry type should have a corresponding schema."""
        for entry_type in ENTRY_TYPES:
            assert entry_type in SCHEMA_REGISTRY


class TestNormalizeExperience:
    """Test experience entry normalization."""

    def test_normalize_standard_fields(self, sample_experience_data):
        """Standard experience fields should be normalized correctly."""
        result = normalize_experience(sample_experience_data)
        
        assert result["role"] == "Software Engineer"
        assert result["company"] == "Tech Corp"
        assert result["location"] == "San Francisco, CA"
        assert result["start_date"] == "2020"
        assert result["end_date"] == "2023"
        assert result["highlights"] == ["Built microservices", "Led team of 5"]

    def test_normalize_dates_computed(self, sample_experience_data):
        """_dates should be computed from start/end dates."""
        result = normalize_experience(sample_experience_data)
        assert result["_dates"] == "2020 - 2023"

    def test_normalize_present_end_date(self):
        """End date should default to 'Present' if not provided."""
        data = {"role": "Engineer", "start_date": "2022"}
        result = normalize_experience(data)
        assert result["_dates"] == "2022 - Present"

    def test_normalize_legacy_fields(self):
        """Legacy field names should be mapped correctly."""
        data = {
            "title": "Developer",  # legacy for role
            "org": "Company",      # legacy for company
            "from": "2020",        # legacy for start_date
            "to": "2022"           # legacy for end_date
        }
        result = normalize_experience(data)
        assert result["role"] == "Developer"
        assert result["company"] == "Company"
        assert result["_dates"] == "2020 - 2022"


class TestNormalizeEducation:
    """Test education entry normalization."""

    def test_normalize_standard_fields(self, sample_education_data):
        """Standard education fields should be normalized correctly."""
        result = normalize_education(sample_education_data)
        
        assert result["school"] == "MIT"
        assert result["degree"] == "BSc Computer Science"
        assert result["gpa"] == "3.9/4.0"

    def test_normalize_legacy_institution(self):
        """'institution' should map to 'school'."""
        data = {"institution": "Stanford", "degree": "PhD"}
        result = normalize_education(data)
        assert result["school"] == "Stanford"


class TestNormalizeSkill:
    """Test skill entry normalization."""

    def test_normalize_category_with_items(self, sample_skill_data):
        """Skills with category and items should normalize correctly."""
        result = normalize_skill(sample_skill_data)
        
        assert result["category"] == "Programming Languages"
        assert result["skill_list"] == ["Python", "JavaScript", "Go", "Rust"]

    def test_normalize_single_skill(self):
        """Single skill with level should normalize correctly."""
        data = {"name": "Python", "level": "Expert"}
        result = normalize_skill(data)
        
        assert result["name"] == "Python"
        assert result["level"] == "Expert"

    def test_normalize_legacy_items_field(self):
        """Legacy 'items' field should map to 'skill_list'."""
        data = {"category": "Languages", "items": ["Python", "Go"]}
        result = normalize_skill(data)
        assert result["skill_list"] == ["Python", "Go"]


class TestNormalizeProject:
    """Test project entry normalization."""

    def test_normalize_standard_fields(self):
        """Standard project fields should normalize correctly."""
        data = {
            "name": "Open Source Tool",
            "organization": "GitHub",
            "link": "https://github.com/project",
            "tech_stack": ["Python", "React"],
            "highlights": ["100+ stars", "Used by 50+ companies"]
        }
        result = normalize_project(data)
        
        assert result["name"] == "Open Source Tool"
        assert result["organization"] == "GitHub"
        assert result["tech_stack"] == ["Python", "React"]


class TestNormalizePublication:
    """Test publication entry normalization."""

    def test_normalize_standard_fields(self):
        """Standard publication fields should normalize correctly."""
        data = {
            "title": "ML Paper",
            "authors": "Doe, J. et al.",
            "venue": "NeurIPS 2023",
            "year": "2023"
        }
        result = normalize_publication(data)
        
        assert result["title"] == "ML Paper"
        assert result["authors"] == "Doe, J. et al."
        assert result["venue"] == "NeurIPS 2023"


class TestNormalizeAward:
    """Test award entry normalization."""

    def test_normalize_standard_fields(self):
        """Standard award fields should normalize correctly."""
        data = {
            "title": "Best Paper Award",
            "issuer": "ACM",
            "date": "2023",
            "description": "For outstanding research"
        }
        result = normalize_award(data)
        
        assert result["title"] == "Best Paper Award"
        assert result["issuer"] == "ACM"


class TestNormalizeEntry:
    """Test the generic normalize_entry function."""

    def test_normalize_known_type(self, sample_experience_data):
        """Known entry types should use their specific normalizer."""
        result = normalize_entry("experience", sample_experience_data)
        assert result["role"] == "Software Engineer"

    def test_normalize_unknown_type(self):
        """Unknown types should use fallback normalization."""
        data = {"title": "Custom Entry", "description": "Some data"}
        result = normalize_entry("custom_type", data)
        assert result["title"] == "Custom Entry"


class TestValidation:
    """Test entry validation."""

    def test_validate_valid_experience(self, sample_experience_data):
        """Valid experience data should pass validation."""
        is_valid, errors = validate_entry("experience", sample_experience_data)
        assert is_valid is True
        assert errors == []

    def test_validate_unknown_type_accepts_any(self):
        """Unknown types should accept any data."""
        is_valid, errors = validate_entry("unknown_type", {"any": "data"})
        assert is_valid is True


class TestSchemaMetadata:
    """Test schema metadata for UI."""

    def test_get_default_data(self):
        """Default data should have all schema fields."""
        defaults = get_default_data("experience")
        assert "role" in defaults
        assert "company" in defaults
        assert "highlights" in defaults

    def test_get_all_schemas_for_ui(self):
        """All schemas should be returned with UI metadata."""
        schemas = get_all_schemas_for_ui()
        
        assert "experience" in schemas
        assert "fields" in schemas["experience"]
        assert "default" in schemas["experience"]

