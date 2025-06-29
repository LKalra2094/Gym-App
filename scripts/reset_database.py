# reset_database.py
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.reset_database import reset_database

def main():
    print("--- Starting Database Reset ---")
    try:
        reset_database()
        print("--- Database has been reset successfully. ---")
    except Exception as e:
        print(f"--- An error occurred during database reset: {e} ---")

if __name__ == "__main__":
    main() 