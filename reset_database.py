#!/usr/bin/env python3
"""
Script to reset the database schema for the simplified Ticker.info approach
"""

import os
import logging
from dotenv import load_dotenv
from db_module import DatabaseManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def reset_database():
    """Reset the database schema"""
    try:
        logging.info("🔄 Resetting database schema...")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        if db_manager.fallback_mode:
            logging.error("❌ Cannot reset database in fallback mode")
            return False
        
        # Drop existing tables
        with db_manager.connection.cursor() as cursor:
            logging.info("🗑️ Dropping existing tables...")
            
            # Drop scraped_data table
            cursor.execute("DROP TABLE IF EXISTS scraped_data CASCADE;")
            
            db_manager.connection.commit()
            logging.info("✅ Old tables dropped successfully")
        
        # Recreate tables with new schema
        logging.info("🏗️ Creating new schema...")
        db_manager._create_table_if_not_exists()
        
        logging.info("🎉 Database schema reset completed successfully!")
        return True
        
    except Exception as e:
        logging.error(f"❌ Database reset failed: {str(e)}")
        return False
    finally:
        if 'db_manager' in locals():
            db_manager.close_connection()

if __name__ == "__main__":
    success = reset_database()
    if success:
        logging.info("🚀 Ready to test the new simplified schema!")
    else:
        logging.error("💥 Schema reset failed!")

