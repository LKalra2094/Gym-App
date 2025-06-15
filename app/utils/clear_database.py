from sqlalchemy import text
from app.database import engine, Base
from app.models import *  # Import all models to ensure they are registered with Base

def clear_database():
    """
    Safely clears all data from the database while preserving the schema.
    This function will:
    1. Disable foreign key constraints
    2. Truncate all tables
    3. Re-enable foreign key constraints
    """
    try:
        # Get all table names
        with engine.begin() as connection:
            # Disable foreign key constraints
            connection.execute(text("SET session_replication_role = 'replica';"))
            
            # Get all table names
            result = connection.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """))
            tables = [row[0] for row in result]
            
            # Truncate all tables
            for table in tables:
                connection.execute(text(f'TRUNCATE TABLE "{table}" CASCADE;'))
            
            # Re-enable foreign key constraints
            connection.execute(text("SET session_replication_role = 'origin';"))
            
            print("Successfully cleared all data from the database.")
            
    except Exception as e:
        print(f"Error clearing database: {str(e)}")
        raise

if __name__ == "__main__":
    clear_database() 