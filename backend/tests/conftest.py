"""
Pytest fixtures for backend tests.
"""

import os
import tempfile
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.models import Base


@pytest.fixture(scope="function")
def db_engine():
    """Create a temporary SQLite database for each test."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    
    yield engine
    
    engine.dispose()
    os.unlink(db_path)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a database session for each test."""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def sample_experience_data():
    """Sample experience entry data."""
    return {
        "role": "Software Engineer",
        "company": "Tech Corp",
        "location": "San Francisco, CA",
        "start_date": "2020",
        "end_date": "2023",
        "highlights": ["Built microservices", "Led team of 5"]
    }


@pytest.fixture
def sample_education_data():
    """Sample education entry data."""
    return {
        "school": "MIT",
        "degree": "BSc Computer Science",
        "location": "Cambridge, MA",
        "start_date": "2016",
        "end_date": "2020",
        "gpa": "3.9/4.0"
    }


@pytest.fixture
def sample_skill_data():
    """Sample skill entry data."""
    return {
        "category": "Programming Languages",
        "skill_list": ["Python", "JavaScript", "Go", "Rust"]
    }


@pytest.fixture
def sample_profile_data():
    """Sample profile data."""
    return {
        "personal": {"full_name": "John Doe"},
        "links": {
            "email": "john@example.com",
            "github": "https://github.com/johndoe",
            "linkedin": "https://linkedin.com/in/johndoe"
        },
        "content": {
            "summary": "Experienced software engineer",
            "tagline": "Building great software"
        }
    }

