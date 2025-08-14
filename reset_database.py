#!/usr/bin/env python3
"""
Script to reset the database and recreate tables with proper schema
"""

import logging
from db_module import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def reset_database():
    """Reset the database by dropping and recreating tables"""
    try:
        print("🗑️  Starting database reset...")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        if db_manager.fallback_mode:
            print("❌ Cannot reset database - running in fallback mode")
            return False
        
        print("🔧 Dropping existing tables...")
        
        # Drop the existing table
        with db_manager.connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS scraped_data CASCADE;")
            db_manager.connection.commit()
            print("✅ Dropped existing scraped_data table")
        
        print("🔧 Recreating tables with new schema...")
        
        # Recreate the table with the new schema
        db_manager._create_table_if_not_exists()
        
        print("✅ Database reset completed successfully!")
        print("📊 New schema includes:")
        print("   - Market cap and enterprise value: NUMERIC(20,2)")
        print("   - Financial ratios: DECIMAL(15,4)")
        print("   - Better handling of large numbers and infinite values")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        logging.error(f"Database reset error: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Database Reset Tool")
    print("=" * 50)
    
    # Confirm before proceeding
    response = input("⚠️  This will DELETE ALL DATA and recreate tables. Continue? (y/N): ")
    if response.lower() != 'y':
        print("❌ Operation cancelled")
        return
    
    # Reset the database
    success = reset_database()
    
    if success:
        print("\n🎉 Database reset completed successfully!")
        print("💡 You can now run your scraper without numeric overflow errors")
    else:
        print("\n❌ Database reset failed. Check logs for details.")

if __name__ == "__main__":
    main()

