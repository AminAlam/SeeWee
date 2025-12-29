"""
Unit tests for exporters.
"""

from datetime import datetime

import pytest
from core.document_model import Document, DocSection, DocItem
from core.exporters.latex_exporter import render_latex_template, _tex_escape
from core.exporters.html_exporter import render_academicpages_like_preview, render_html_bundle
from core.exporters.linkedin_exporter import render_linkedin_bundle


class TestTexEscape:
    """Test LaTeX character escaping."""

    def test_escape_ampersand(self):
        """& should be escaped to \\&."""
        assert _tex_escape("A & B") == r"A \& B"

    def test_escape_percent(self):
        """% should be escaped to \\%."""
        assert _tex_escape("100%") == r"100\%"

    def test_escape_dollar(self):
        """$ should be escaped to \\$."""
        assert _tex_escape("$100") == r"\$100"

    def test_escape_hash(self):
        """# should be escaped to \\#."""
        assert _tex_escape("#1") == r"\#1"

    def test_escape_underscore(self):
        """_ should be escaped to \\_."""
        assert _tex_escape("var_name") == r"var\_name"

    def test_escape_braces(self):
        """{} should be escaped to \\{\\}."""
        assert _tex_escape("{test}") == r"\{test\}"

    def test_no_escape_normal_text(self):
        """Normal text should not be modified."""
        assert _tex_escape("Hello World") == "Hello World"


class TestLatexExporter:
    """Test LaTeX template rendering."""

    @pytest.fixture
    def sample_document(self, sample_experience_data, sample_education_data):
        """Create a sample document for testing."""
        return Document(
            variant_id="test-variant",
            generated_at=datetime.now(),
            sections=[
                DocSection(
                    id="experience",
                    title="Experience",
                    items=[
                        DocItem(
                            entry_id="exp-1",
                            entry_type="experience",
                            data=sample_experience_data,
                            tags=["work"]
                        )
                    ]
                ),
                DocSection(
                    id="education",
                    title="Education",
                    items=[
                        DocItem(
                            entry_id="edu-1",
                            entry_type="education",
                            data=sample_education_data,
                            tags=["school"]
                        )
                    ]
                )
            ]
        )

    @pytest.fixture
    def sample_profile(self, sample_profile_data):
        """Sample profile for testing."""
        return sample_profile_data

    def test_render_includes_name(self, sample_document, sample_profile):
        """Rendered LaTeX should include the full name."""
        tex = render_latex_template(sample_document, sample_profile)
        assert "John Doe" in tex

    def test_render_includes_sections(self, sample_document, sample_profile):
        """Rendered LaTeX should include section content."""
        tex = render_latex_template(sample_document, sample_profile)
        assert "Software Engineer" in tex
        assert "MIT" in tex

    def test_render_includes_contact_info(self, sample_document, sample_profile):
        """Rendered LaTeX should include contact info."""
        tex = render_latex_template(sample_document, sample_profile)
        assert "john@example.com" in tex
        assert "GitHub" in tex

    def test_render_is_valid_latex(self, sample_document, sample_profile):
        """Rendered output should be valid LaTeX structure."""
        tex = render_latex_template(sample_document, sample_profile)
        assert r"\documentclass" in tex
        assert r"\begin{document}" in tex
        assert r"\end{document}" in tex

    def test_render_empty_document(self, sample_profile):
        """Empty document should still render valid LaTeX."""
        doc = Document(variant_id="empty", generated_at=datetime.now(), sections=[])
        tex = render_latex_template(doc, sample_profile)
        assert r"\documentclass" in tex
        assert r"\end{document}" in tex


class TestHtmlExporter:
    """Test HTML exporter."""

    @pytest.fixture
    def sample_document(self, sample_experience_data):
        """Create a sample document for testing."""
        return Document(
            variant_id="test-variant",
            generated_at=datetime.now(),
            sections=[
                DocSection(
                    id="experience",
                    title="Experience",
                    items=[
                        DocItem(
                            entry_id="exp-1",
                            entry_type="experience",
                            data=sample_experience_data,
                            tags=["work"]
                        )
                    ]
                )
            ]
        )

    @pytest.fixture
    def sample_profile(self, sample_profile_data):
        return sample_profile_data

    def test_academic_preview_includes_name(self, sample_document, sample_profile):
        """Academic preview should include name."""
        html = render_academicpages_like_preview(sample_document, sample_profile)
        assert "John Doe" in html

    def test_academic_preview_includes_sections(self, sample_document, sample_profile):
        """Academic preview should include section data."""
        html = render_academicpages_like_preview(sample_document, sample_profile)
        assert "Software Engineer" in html or "experience" in html.lower()

    def test_academic_preview_is_valid_html(self, sample_document, sample_profile):
        """Academic preview should be valid HTML structure."""
        html = render_academicpages_like_preview(sample_document, sample_profile)
        assert "<!doctype html>" in html.lower() or "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html

    def test_html_bundle_contains_files(self, sample_document):
        """HTML bundle should contain expected files."""
        bundle = render_html_bundle(sample_document)
        assert "index.html" in bundle

    def test_html_bundle_index_is_html(self, sample_document):
        """Bundle index.html should be valid HTML."""
        bundle = render_html_bundle(sample_document)
        html = bundle["index.html"]
        assert "<!doctype html>" in html.lower() or "<!DOCTYPE html>" in html


class TestLinkedInExporter:
    """Test LinkedIn exporter."""

    @pytest.fixture
    def sample_document(self, sample_experience_data, sample_skill_data):
        """Create a sample document for testing."""
        return Document(
            variant_id="test-variant",
            generated_at=datetime.now(),
            sections=[
                DocSection(
                    id="experience",
                    title="Experience",
                    items=[
                        DocItem(
                            entry_id="exp-1",
                            entry_type="experience",
                            data=sample_experience_data,
                            tags=[]
                        )
                    ]
                ),
                DocSection(
                    id="skills",
                    title="Skills",
                    items=[
                        DocItem(
                            entry_id="skill-1",
                            entry_type="skill",
                            data=sample_skill_data,
                            tags=[]
                        )
                    ]
                )
            ]
        )

    def test_linkedin_bundle_contains_files(self, sample_document):
        """LinkedIn bundle should contain expected files."""
        bundle = render_linkedin_bundle(sample_document)
        assert len(bundle) > 0
        # Check for at least one text file
        assert any(name.endswith('.txt') or name.endswith('.md') for name in bundle.keys())
