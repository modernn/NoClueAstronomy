"""
Database initialization script.

This script initializes the database by creating all tables
and setting up initial data if needed.
"""

import logging
import os
import sys

# Add parent directory to path to allow running this script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.models.db import Base, engine, get_db
from api.config import validate_config

# Configure logging
logger = logging.getLogger(__name__)

def init_db():
    """
    Initialize the database by creating all tables.
    """
    # Validate configuration
    validate_config()
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Optionally seed initial data here
        # seed_initial_data()
        
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def seed_initial_data():
    """
    Seed the database with initial data.
    
    This function is called after creating the tables to populate
    the database with any required initial data.
    """
    db = next(get_db())
    try:
        # Add your seeding logic here
        # Example:
        # db.add(SomeModel(field1="value1", field2="value2"))
        
        db.commit()
        logger.info("Initial data seeded successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding initial data: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialization complete")