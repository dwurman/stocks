#!/usr/bin/env python3
"""
Debug script to test database insertion with just 1 ticker
"""

import logging
import json
from datetime import datetime
from yfinance_api_scraper import YahooFinanceAPIScraper
from db_module import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more detailed output
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Test with just 1 ticker to debug database insertion"""
    try:
        # Initialize the scraper and database
        logging.info("🚀 Initializing Yahoo Finance API scraper and database...")
        scraper = YahooFinanceAPIScraper()
        db = DatabaseManager()
        
        # Test with just 1 ticker
        test_ticker = 'AAPL'
        logging.info(f"📊 Testing with single ticker: {test_ticker}")
        
        # Fetch data for the single ticker
        logging.info("🔄 Fetching data...")
        ticker_data = scraper._get_single_ticker_info(test_ticker)
        
        if ticker_data:
            logging.info(f"✅ Data fetched successfully for {test_ticker}")
            logging.info(f"   Data keys: {list(ticker_data.keys())}")
            logging.info(f"   Data structure: {list(ticker_data.get('data', {}).keys())[:10]}...")
            
            # Save the raw data to a file for inspection
            with open(f'debug_{test_ticker}_raw_data.json', 'w') as f:
                json.dump(ticker_data, f, indent=2, default=str)
            logging.info(f"💾 Raw data saved to debug_{test_ticker}_raw_data.json")
            
            # Try to save to database
            logging.info("💾 Attempting to save to database...")
            try:
                save_success = db.save_batch_ticker_data([ticker_data])
                logging.info(f"Database save result: {save_success}")
                
                if save_success:
                    logging.info("✅ Successfully saved to database!")
                else:
                    logging.error("❌ Failed to save to database")
                    
            except Exception as db_error:
                logging.error(f"❌ Database error: {db_error}")
                logging.error(f"Error type: {type(db_error)}")
                import traceback
                logging.error(f"Traceback: {traceback.format_exc()}")
            
            # Also try individual save method
            logging.info("🔄 Trying individual save method...")
            try:
                individual_success = db.save_ticker_data(ticker_data)
                logging.info(f"Individual save result: {individual_success}")
            except Exception as individual_error:
                logging.error(f"❌ Individual save error: {individual_error}")
                import traceback
                logging.error(f"Traceback: {traceback.format_exc()}")
            
        else:
            logging.error(f"❌ No data fetched for {test_ticker}")
            
    except Exception as e:
        logging.error(f"❌ Fatal error: {e}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise
    finally:
        # Close database connection
        if 'db' in locals():
            db.close_connection()
            logging.info("🔌 Database connection closed")

if __name__ == "__main__":
    main()
