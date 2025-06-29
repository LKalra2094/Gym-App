# app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import make_url
from app.core.config import settings

# Make the database URL compatible with psycopg2
db_url = make_url(str(settings.DATABASE_URL))
db_url = db_url.set(drivername="postgresql+psycopg2")

# Create a synchronous engine
engine = create_engine(db_url, pool_pre_ping=True)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency to get a DB session.
    Ensures the session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
