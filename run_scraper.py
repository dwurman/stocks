#!/usr/bin/env python3
"""
Main runner script for Yahoo Finance scraper
Loads tickers from file, runs scraper, and saves data to database
"""

import os
import sys
import logging
import time
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
        logging.StreamHandler(),
        logging.FileHandler('scraper_run.log')
    ]
)

def load_tickers_from_file(filename='stocks.txt'):
    """Load stock tickers from a text file"""
    try:
        if not os.path.exists(filename):
            logging.error(f"Ticker file {filename} not found")
            return []
        
        with open(filename, 'r') as file:
            tickers = []
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    tickers.append(line.upper())
        
        logging.info(f"Loaded {len(tickers)} tickers from {filename}")
        return tickers
        
    except Exception as e:
        logging.error(f"Error loading tickers from {filename}: {str(e)}")
        return []

def run_scraper_for_ticker(scraper, ticker):
    """Run the scraper for a single ticker and return the data"""
    try:
        logging.info(f"Starting to scrape {ticker}")
        
        # Step 1: Scrape the website
        html_content = scraper.scrape_website(ticker)
        
        if not html_content:
            logging.error(f"Failed to retrieve page content for {ticker}")
            return None
        
        # Step 2: Parse the content
        ticker_data = scraper.parse_yahoo_finance_content(html_content, ticker)
        
        if ticker_data:
            logging.info(f"Successfully processed {ticker}")
            return ticker_data
        else:
            logging.warning(f"No data extracted for {ticker}")
            return None
            
    except Exception as e:
        logging.error(f"Error processing {ticker}: {str(e)}")
        return None

def main():
    """Main function to run the scraper for all tickers and save to database"""
    scraper = None
    db_manager = None
    
    try:
        # Initialize scraper
        logging.info("Initializing Yahoo Finance scraper...")
        scraper = YahooFinanceScraper()
        
        # Initialize database manager
        logging.info("Initializing database manager...")
        try:
            db_manager = DatabaseManager()
            if db_manager.fallback_mode:
                logging.warning("Database manager is in fallback mode - data will not be saved to database")
            else:
                logging.info("Database manager initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize database manager: {str(e)}")
            logging.warning("Continuing without database functionality")
            db_manager = None
        
        # Load tickers from file
        tickers = load_tickers_from_file()
        if not tickers:
            logging.error("No tickers loaded. Exiting.")
            return
        
        logging.info(f"Starting scraping job for {len(tickers)} tickers")
        
        # Process each ticker
        all_data = []
        successful_scrapes = 0
        
        for i, ticker in enumerate(tickers, 1):
            logging.info(f"Processing ticker {i}/{len(tickers)}: {ticker}")
            
            # Run scraper for this ticker
            ticker_data = run_scraper_for_ticker(scraper, ticker)
            
            if ticker_data:
                all_data.append(ticker_data)
                successful_scrapes += 1
                
                # Show extracted data summary
                data_keys = list(ticker_data.get('data', {}).keys())
                logging.info(f"Extracted data for {ticker}: {data_keys}")
                
                # Save to database immediately
                if db_manager:
                    success = db_manager.save_ticker_data(ticker_data)
                    if success:
                        logging.info(f"Successfully saved {ticker} to database")
                    else:
                        logging.error(f"Failed to save {ticker} to database")
            
            # Add delay between requests to be respectful
            if i < len(tickers):  # Don't sleep after the last ticker
                time.sleep(2)
        
        # Summary
        logging.info(f"Scraping job completed!")
        logging.info(f"Successfully scraped: {successful_scrapes}/{len(tickers)} tickers")
        
        if successful_scrapes > 0:
            # Save all data to database (as a backup to individual saves)
            if db_manager:
                save_results = db_manager.save_multiple_tickers(all_data)
                logging.info(f"Database save results: {save_results}")
            
            # Optional: Show sample of extracted data
            if all_data:
                sample_ticker = all_data[0]
                logging.info(f"Sample data structure for {sample_ticker['ticker']}:")
                for key, value in sample_ticker.get('data', {}).items():
                    if isinstance(value, dict):
                        logging.info(f"  {key}: {list(value.keys())}")
                    else:
                        logging.info(f"  {key}: {value}")
        
    except KeyboardInterrupt:
        logging.info("Scraper stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        raise
    finally:
        logging.info("Scraper run completed")

def run_scheduled():
    """Run the scraper on a schedule (for production use)"""
    import schedule
    
    logging.info("Setting up scheduled scraping job...")
    
    # Schedule to run every day at 9 AM
    schedule.every().day.at("09:00").do(main)
    
    # Also run immediately
    main()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--scheduled":
        run_scheduled()
    else:
        main()
