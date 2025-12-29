"""
Unit tests for the variant engine.
"""

import pytest
from datetime import datetime

from core.document_model import Document, DocSection, DocItem
from core.repos.entries_repo import EntriesRepo
from core.repos.variants_repo import VariantsRepo


class TestVariantEngine:
    """Test variant engine functionality."""

    def test_document_structure(self, sample_experience_data):
        """Test creating a Document with proper structure."""
        doc = Document(
            variant_id="test-id",
            generated_at=datetime.now(),
            sections=[
                DocSection(
                    id="experience",
                    title="Experience",
                    items=[
                        DocItem(
                            entry_id="e1",
                            entry_type="experience",
                            data=sample_experience_data,
                            tags=["work"]
                        )
                    ]
                )
            ]
        )
        
        assert doc.variant_id == "test-id"
        assert len(doc.sections) == 1
        assert doc.sections[0].id == "experience"
        assert len(doc.sections[0].items) == 1

    def test_doc_section_structure(self, sample_experience_data):
        """Test DocSection structure."""
        section = DocSection(
            id="experience",
            title="Work Experience",
            items=[
                DocItem(
                    entry_id="e1",
                    entry_type="experience",
                    data=sample_experience_data,
                    tags=[]
                )
            ]
        )
        
        assert section.id == "experience"
        assert section.title == "Work Experience"
        assert len(section.items) == 1

    def test_doc_item_structure(self, sample_experience_data):
        """Test DocItem structure."""
        item = DocItem(
            entry_id="e1",
            entry_type="experience",
            data=sample_experience_data,
            tags=["work", "tech"]
        )
        
        assert item.entry_id == "e1"
        assert item.entry_type == "experience"
        assert item.data["role"] == "Software Engineer"
        assert "work" in item.tags

    def test_empty_document(self):
        """Test creating an empty document."""
        doc = Document(
            variant_id="empty",
            generated_at=datetime.now(),
            sections=[]
        )
        
        assert doc.variant_id == "empty"
        assert doc.sections == []

    def test_multiple_sections(self, sample_experience_data, sample_education_data):
        """Test document with multiple sections."""
        doc = Document(
            variant_id="multi",
            generated_at=datetime.now(),
            sections=[
                DocSection(
                    id="experience",
                    title="Experience",
                    items=[
                        DocItem(
                            entry_id="e1",
                            entry_type="experience",
                            data=sample_experience_data,
                            tags=[]
                        )
                    ]
                ),
                DocSection(
                    id="education",
                    title="Education",
                    items=[
                        DocItem(
                            entry_id="e2",
                            entry_type="education",
                            data=sample_education_data,
                            tags=[]
                        )
                    ]
                )
            ]
        )
        
        assert len(doc.sections) == 2
        section_ids = [s.id for s in doc.sections]
        assert "experience" in section_ids
        assert "education" in section_ids

    def test_section_with_multiple_items(self, sample_experience_data):
        """Test section with multiple items."""
        experience2 = {**sample_experience_data, "role": "Senior Engineer"}
        
        section = DocSection(
            id="experience",
            title="Experience",
            items=[
                DocItem(entry_id="e1", entry_type="experience", data=sample_experience_data, tags=[]),
                DocItem(entry_id="e2", entry_type="experience", data=experience2, tags=[])
            ]
        )
        
        assert len(section.items) == 2
        assert section.items[0].data["role"] == "Software Engineer"
        assert section.items[1].data["role"] == "Senior Engineer"
