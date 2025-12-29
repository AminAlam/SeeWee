"""
Unit tests for repository classes.
"""

import pytest
from sqlalchemy.exc import NoResultFound

from core.repos.entries_repo import EntriesRepo
from core.repos.variants_repo import VariantsRepo
from core.repos.profile_repo import ProfileRepo
from core.repos.tags_repo import TagsRepo


class TestEntriesRepo:
    """Test EntriesRepo functionality."""

    def test_create_entry(self, db_session, sample_experience_data):
        """Creating an entry should return the created record."""
        repo = EntriesRepo(db_session)
        
        entry = repo.create(
            entry_type="experience",
            data=sample_experience_data,
            tags=["work", "tech"]
        )
        
        assert entry.id is not None
        assert entry.type == "experience"
        assert entry.data["role"] == "Software Engineer"
        assert set(entry.tags) == {"work", "tech"}

    def test_get_entry(self, db_session, sample_experience_data):
        """Getting an entry by ID should return it."""
        repo = EntriesRepo(db_session)
        created = repo.create(entry_type="experience", data=sample_experience_data)
        
        fetched = repo.get(created.id)
        
        assert fetched.id == created.id
        assert fetched.data == created.data

    def test_get_entry_not_found(self, db_session):
        """Getting a non-existent entry should raise NoResultFound."""
        repo = EntriesRepo(db_session)
        
        with pytest.raises(NoResultFound):
            repo.get("non-existent-id")

    def test_list_entries(self, db_session, sample_experience_data, sample_education_data):
        """Listing entries should return all entries."""
        repo = EntriesRepo(db_session)
        repo.create(entry_type="experience", data=sample_experience_data)
        repo.create(entry_type="education", data=sample_education_data)
        
        entries = repo.list()
        
        assert len(entries) == 2

    def test_list_entries_by_type(self, db_session, sample_experience_data, sample_education_data):
        """Listing entries by type should filter correctly."""
        repo = EntriesRepo(db_session)
        repo.create(entry_type="experience", data=sample_experience_data)
        repo.create(entry_type="education", data=sample_education_data)
        
        experiences = repo.list(entry_type="experience")
        
        assert len(experiences) == 1
        assert experiences[0].type == "experience"

    def test_update_entry(self, db_session, sample_experience_data):
        """Updating an entry should modify its data."""
        repo = EntriesRepo(db_session)
        created = repo.create(entry_type="experience", data=sample_experience_data)
        
        updated_data = {**sample_experience_data, "role": "Senior Engineer"}
        updated = repo.update(created.id, data=updated_data)
        
        assert updated.data["role"] == "Senior Engineer"

    def test_delete_entry(self, db_session, sample_experience_data):
        """Deleting an entry should remove it from the database."""
        repo = EntriesRepo(db_session)
        created = repo.create(entry_type="experience", data=sample_experience_data)
        
        repo.delete(created.id)
        
        with pytest.raises(NoResultFound):
            repo.get(created.id)


class TestVariantsRepo:
    """Test VariantsRepo functionality."""

    def test_create_variant(self, db_session):
        """Creating a variant should return the created record."""
        repo = VariantsRepo(db_session)
        
        variant = repo.create(
            name="Academic CV",
            rules={"max_items": 10},
            sections=["education", "publications", "awards"]
        )
        
        assert variant.id is not None
        assert variant.name == "Academic CV"

    def test_get_variant(self, db_session):
        """Getting a variant by ID should return it."""
        repo = VariantsRepo(db_session)
        created = repo.create(name="Test", rules={}, sections=["experience"])
        
        fetched = repo.get(created.id)
        
        assert fetched.id == created.id
        assert fetched.name == "Test"

    def test_list_variants(self, db_session):
        """Listing variants should return all variants."""
        repo = VariantsRepo(db_session)
        repo.create(name="Variant 1", rules={}, sections=["experience"])
        repo.create(name="Variant 2", rules={}, sections=["education"])
        
        variants = repo.list()
        
        assert len(variants) == 2

    def test_update_variant_name(self, db_session):
        """Updating a variant name should modify it."""
        repo = VariantsRepo(db_session)
        created = repo.create(name="Old Name", rules={}, sections=["experience"])
        
        updated = repo.update(created.id, name="New Name")
        
        assert updated.name == "New Name"

    def test_delete_variant(self, db_session):
        """Deleting a variant should remove it."""
        repo = VariantsRepo(db_session)
        created = repo.create(name="To Delete", rules={}, sections=["experience"])
        
        repo.delete(created.id)
        
        with pytest.raises(NoResultFound):
            repo.get(created.id)


class TestProfileRepo:
    """Test ProfileRepo functionality."""

    def test_get_creates_default(self, db_session):
        """Getting profile when none exists should create default."""
        repo = ProfileRepo(db_session)
        
        profile = repo.get()
        
        assert profile is not None
        assert profile.data == {}

    def test_put_profile(self, db_session, sample_profile_data):
        """Putting profile should modify its data."""
        repo = ProfileRepo(db_session)
        
        updated = repo.put(sample_profile_data)
        
        assert updated.data["personal"]["full_name"] == "John Doe"
        assert updated.data["links"]["email"] == "john@example.com"

    def test_get_after_put(self, db_session, sample_profile_data):
        """Getting profile after put should return updated data."""
        repo = ProfileRepo(db_session)
        repo.put(sample_profile_data)
        
        profile = repo.get()
        
        assert profile.data["personal"]["full_name"] == "John Doe"


class TestTagsRepo:
    """Test TagsRepo functionality."""

    def test_list_tags_empty(self, db_session):
        """Listing tags with no entries should return empty."""
        repo = TagsRepo(db_session)
        
        tags = repo.list()
        
        assert tags == []

    def test_list_tags_from_entries(self, db_session, sample_experience_data):
        """Tags should be collected from all entries."""
        entries_repo = EntriesRepo(db_session)
        entries_repo.create(
            entry_type="experience",
            data=sample_experience_data,
            tags=["work", "tech"]
        )
        entries_repo.create(
            entry_type="experience",
            data=sample_experience_data,
            tags=["work", "startup"]
        )
        
        tags_repo = TagsRepo(db_session)
        tags = tags_repo.list()
        
        assert set(tags) == {"work", "tech", "startup"}
