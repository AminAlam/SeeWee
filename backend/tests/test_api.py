"""
Integration tests for API endpoints.
"""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from api.db import db_session
from core.models import Base


@pytest.fixture(scope="function")
def test_db():
    """Create a temporary database for API tests."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    
    yield SessionLocal
    
    engine.dispose()
    try:
        os.unlink(db_path)
    except Exception:
        pass


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with overridden database."""
    def override_db():
        session = test_db()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    app.dependency_overrides[db_session] = override_db
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_returns_ok(self, client):
        """Health endpoint should return status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestEntriesAPI:
    """Test entries API endpoints."""

    def test_list_entries_empty(self, client):
        """Listing entries when empty should return empty list."""
        response = client.get("/api/v1/entries")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_entry(self, client, sample_experience_data):
        """Creating an entry should return the created entry."""
        response = client.post("/api/v1/entries", json={
            "type": "experience",
            "data": sample_experience_data,
            "tags": ["work"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "experience"
        assert data["data"]["role"] == "Software Engineer"
        assert "id" in data

    def test_get_entry_not_found(self, client):
        """Getting non-existent entry should return 404."""
        response = client.get("/api/v1/entries/non-existent")
        assert response.status_code == 404

    def test_create_and_list_entries(self, client, sample_experience_data):
        """Creating entries and listing them should work."""
        # Create entry
        client.post("/api/v1/entries", json={
            "type": "experience",
            "data": sample_experience_data,
            "tags": []
        })
        
        # List entries
        response = client.get("/api/v1/entries")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestVariantsAPI:
    """Test variants API endpoints."""

    def test_list_variants_empty(self, client):
        """Listing variants when empty should return empty list."""
        response = client.get("/api/v1/variants")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_variant(self, client):
        """Creating a variant should return the created variant."""
        response = client.post("/api/v1/variants", json={
            "name": "Academic CV",
            "rules": {},
            "sections": ["education", "publications"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Academic CV"
        assert "id" in data

    def test_get_variant_not_found(self, client):
        """Getting non-existent variant should return 404."""
        response = client.get("/api/v1/variants/non-existent")
        assert response.status_code == 404


class TestProfileAPI:
    """Test profile API endpoints."""

    def test_get_profile_default(self, client):
        """Getting profile when none set should return default."""
        response = client.get("/api/v1/profile")
        assert response.status_code == 200
        assert "data" in response.json()

    def test_update_profile(self, client, sample_profile_data):
        """Updating profile should persist changes."""
        response = client.put("/api/v1/profile", json={
            "data": sample_profile_data
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["personal"]["full_name"] == "John Doe"


class TestTagsAPI:
    """Test tags API endpoints."""

    def test_list_tags_empty(self, client):
        """Listing tags when no entries should return empty."""
        response = client.get("/api/v1/tags")
        assert response.status_code == 200
        assert response.json() == []
