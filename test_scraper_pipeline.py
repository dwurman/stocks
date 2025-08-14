#!/usr/bin/env python3
"""
Test script to verify the complete scraper pipeline:
1. Load first ticker from stocks.txt
2. Scrape Yahoo Finance data
3. Save to PostgreSQL database
"""

import os
import sys
import logging
import json
from datetime import datetime
from dotenv import load_dotenv

# Import our modules
from scraper import YahooFinanceScraper
from db_module import DatabaseManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def load_first_ticker(filename='stocks.txt'):
    """Load the first stock ticker from the file"""
    try:
        if not os.path.exists(filename):
            logging.error(f"Ticker file {filename} not found")
            return None
        
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    ticker = line.upper()
                    logging.info(f"Selected first ticker: {ticker}")
                    return ticker
        
        logging.error("No valid tickers found in file")
        return None
        
    except Exception as e:
        logging.error(f"Error loading ticker from {filename}: {str(e)}")
        return None

def test_scraper_pipeline():
    """Test the complete scraper pipeline with one ticker"""
    scraper = None
    db_manager = None
    
    try:
        # Step 1: Load first ticker
        logging.info("=" * 60)
        logging.info("🧪 TESTING COMPLETE SCRAPER PIPELINE")
        logging.info("=" * 60)
        
        ticker = load_first_ticker()
        if not ticker:
            logging.error("Failed to load ticker. Exiting.")
            return False
        
        # Step 2: Initialize scraper
        logging.info(f"📊 Initializing Yahoo Finance scraper...")
        scraper = YahooFinanceScraper()
        
        # Step 3: Initialize database manager
        logging.info(f"🗄️ Initializing database manager...")
        db_manager = DatabaseManager()
        
        if db_manager.fallback_mode:
            logging.warning("⚠️ Database manager is in fallback mode - data will not be saved")
            return False
        
        # Step 4: Scrape the ticker
        logging.info(f"🔍 Starting to scrape {ticker}...")
        html_content = scraper.scrape_website(ticker)
        
        if not html_content:
            logging.error(f"❌ Failed to retrieve analysis page content for {ticker}")
            return False
        
        # Step 4b: Scrape the summary page
        logging.info(f"🔍 Starting to scrape summary page for {ticker}...")
        summary_html_content = scraper.scrape_summary_page(ticker)
        
        if not summary_html_content:
            logging.warning(f"⚠️ Failed to retrieve summary page content for {ticker}, continuing with analysis data only")
        
        # Step 5: Parse the content
        logging.info(f"🔧 Parsing scraped content...")
        ticker_data = scraper.parse_yahoo_finance_content(html_content, ticker, summary_html_content)
        
        if not ticker_data:
            logging.error(f"❌ No data extracted for {ticker}")
            return False
        
        # Step 6: Display extracted data summary
        logging.info(f"✅ Successfully extracted data for {ticker}")
        logging.info(f"📋 Data structure:")
        logging.info(f"   - Ticker: {ticker_data['ticker']}")
        logging.info(f"   - Scraped at: {ticker_data['scraped_at']}")
        logging.info(f"   - URL: {ticker_data['url']}")
        logging.info(f"   - Data keys: {list(ticker_data.get('data', {}).keys())}")
        
        # Show detailed data structure
        for key, value in ticker_data.get('data', {}).items():
            if isinstance(value, dict):
                logging.info(f"   - {key}: {list(value.keys())}")
            else:
                logging.info(f"   - {key}: {value}")
        
        # Step 7: Save to database
        logging.info(f"💾 Saving data to database...")
        success = db_manager.save_ticker_data(ticker_data)
        
        if success:
            logging.info(f"🎉 SUCCESS: Data for {ticker} saved to database!")
            
            # Step 8: Verify data was saved by retrieving it
            logging.info(f"🔍 Verifying data retrieval...")
            history = db_manager.get_ticker_history(ticker, limit=1)
            
            if history:
                saved_record = history[0]
                logging.info(f"✅ Data verification successful!")
                logging.info(f"   - Database ID: {saved_record['id']}")
                logging.info(f"   - Saved at: {saved_record['created_at']}")
                
                # Show the structure of saved data
                logging.info(f"   - Price data:")
                logging.info(f"     * Current: ${saved_record.get('price_current', 'N/A')}")
                logging.info(f"     * Low: ${saved_record.get('price_low', 'N/A')}")
                logging.info(f"     * High: ${saved_record.get('price_high', 'N/A')}")
                logging.info(f"     * Average: ${saved_record.get('price_average', 'N/A')}")
                logging.info(f"     * Percent: {saved_record.get('price_percent', 'N/A')}%")
                
                # Show quote statistics data
                logging.info(f"   - Quote statistics:")
                logging.info(f"     * Previous Close: ${saved_record.get('previous_close', 'N/A')}")
                logging.info(f"     * Open: ${saved_record.get('open_price', 'N/A')}")
                logging.info(f"     * Day Range: {saved_record.get('day_low', 'N/A')} - {saved_record.get('day_high', 'N/A')}")
                logging.info(f"     * 52 Week Range: {saved_record.get('week_52_low', 'N/A')} - {saved_record.get('week_52_high', 'N/A')}")
                logging.info(f"     * Volume: {saved_record.get('volume', 'N/A'):,}" if saved_record.get('volume') else "     * Volume: N/A")
                logging.info(f"     * Market Cap: {saved_record.get('market_cap', 'N/A')}")
                logging.info(f"     * Beta: {saved_record.get('beta', 'N/A')}")
                logging.info(f"     * PE Ratio: {saved_record.get('pe_ratio_ttm', 'N/A')}")
                logging.info(f"     * EPS: {saved_record.get('eps_ttm', 'N/A')}")
                logging.info(f"     * Target 1Y: ${saved_record.get('target_1y', 'N/A')}")
                
                return True
            else:
                logging.warning(f"⚠️ Could not retrieve saved data for verification")
                return False
            
        else:
            logging.error(f"❌ FAILED: Could not save data for {ticker} to database")
            return False
        
    except Exception as e:
        logging.error(f"❌ Pipeline test failed with error: {str(e)}")
        return False
    finally:
        # Clean up
        if db_manager:
            db_manager.close_connection()
        logging.info("🧹 Cleanup completed")

def main():
    """Main test function"""
    logging.info("🚀 Starting scraper pipeline test...")
    
    success = test_scraper_pipeline()
    
    if success:
        logging.info("🎉 PIPELINE TEST PASSED! Everything is working correctly.")
        logging.info("✅ Scraper: Working")
        logging.info("✅ Database: Connected and saving data")
        logging.info("✅ Data extraction: Successful")
        logging.info("✅ Data persistence: Successful")
    else:
        logging.error("❌ PIPELINE TEST FAILED! Check the logs above for issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()
