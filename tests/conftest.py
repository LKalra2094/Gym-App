import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from typing import Generator
import os

from app.main import app
from app.db.session import get_db
from app.core.config import settings
from app.utils.reset_database import reset_database

# Use the database URL from the main app configuration, ensuring it's a string
SQLALCHEMY_DATABASE_URL = str(settings.DATABASE_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Reset and seed the database once per test session.
    This creates the default admin user.
    """
    reset_database()

@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """
    Yields a database session for a single test function.
    This session will have access to the pre-seeded data.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Yields a TestClient for making API requests.
    Overrides the `get_db` dependency to use the test database session.
    """
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear() 