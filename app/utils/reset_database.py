# app/utils/reset_database.py
from datetime import date
from app.db.session import engine, SessionLocal
from app.models.base import Base
from app.core.security import get_password_hash

# Import all models to ensure they are registered with Base.metadata
from app.models.user import User
from app.models.enums import UserRole, Gender
from app.models import Workout, Exercise, ExerciseLog

def reset_database():
    """
    Drops all tables and recreates them based on the current models.
    Also creates a default admin user.
    """
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped.")
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    print("Creating default admin user...")
    db: Session = SessionLocal()
    try:
        admin_user = User(
            email="lakshyakalra123@gmail.com",
            password=get_password_hash("LK@12345678"),
            role=UserRole.ADMIN,
            first_name="Lakshya",
            last_name="Kalra",
            birthday=date(1994, 1, 20),
            gender=Gender.MALE,
            is_verified=True,
        )
        db.add(admin_user)
        db.commit()
        print("Default admin user created successfully.")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close() 