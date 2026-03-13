"""
Database initialization script for CricketIQ.

Creates all tables using SQLAlchemy ORM models.
"""
import sys
import os

# Ensure project root is in path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.db import init_db

def main():
    """Main entry point for DB initialization."""
    print("Starting CricketIQ database initialization...")
    try:
        init_db()
        print("Initialization completed.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
