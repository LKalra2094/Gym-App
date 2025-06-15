import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Workout, Exercise, ExerciseLog
import os
from dotenv import load_dotenv

load_dotenv()

# Use the Supabase database URL
TEST_DATABASE_URL = "postgresql://postgres:Hsb9IPCr3a8cfzHN@db.ynpvwgblyssobuxskufz.supabase.co:5432/postgres"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    # We'll keep the tables after tests since this is a development database
    # Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def db_session(engine):
    """Create a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close() 