#!/usr/bin/env python3
"""
Test script to scrape the first 100 tickers from all_tickers.txt using batches of 10
Optimized for batch processing and database insertion
"""

import logging
import time
from datetime import datetime
from yfinance_api_scraper import YahooFinanceAPIScraper
from db_module import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'test_first_100_tickers_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

def load_tickers_from_file(filename, limit=100):
    """Load tickers from file with a limit"""
    try:
        with open(filename, 'r') as f:
            tickers = [line.strip() for line in f if line.strip()]
        return tickers[:limit]
    except FileNotFoundError:
        logging.error(f"File {filename} not found")
        return []
    except Exception as e:
        logging.error(f"Error reading {filename}: {e}")
        return []

def main():
    """Main function to test first 100 tickers with batch processing"""
    start_time = time.time()
    
    try:
        # Initialize the scraper and database
        logging.info("🚀 Initializing Yahoo Finance API scraper and database...")
        scraper = YahooFinanceAPIScraper()
        db = DatabaseManager()
        
        # Load first 100 tickers
        logging.info("📋 Loading first 100 tickers from all_tickers.txt...")
        tickers = load_tickers_from_file('all_tickers.txt', limit=100)
        
        if not tickers:
            logging.error("❌ No tickers loaded from file")
            return
        
        logging.info(f"✅ Loaded {len(tickers)} tickers: {tickers[:5]}...{tickers[-5:] if len(tickers) > 10 else ''}")
        
        # Process tickers in batches of 10
        batch_size = 10
        total_batches = (len(tickers) + batch_size - 1) // batch_size
        
        logging.info(f"🔄 Starting batch processing: {len(tickers)} tickers in {total_batches} batches of {batch_size}")
        
        all_results = []
        successful_batches = 0
        failed_batches = 0
        
        for batch_num in range(total_batches):
            batch_start_time = time.time()
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(tickers))
            batch_tickers = tickers[start_idx:end_idx]
            
            logging.info(f"🔄 Processing batch {batch_num + 1}/{total_batches}: {len(batch_tickers)} tickers")
            logging.info(f"   Batch tickers: {batch_tickers}")
            
            try:
                # Fetch batch data
                batch_data = scraper.get_batch_tickers_info(batch_tickers, batch_size=batch_size)
                
                if batch_data:
                    logging.info(f"✅ Batch {batch_num + 1} fetched successfully: {len(batch_data)} tickers")
                    
                    # Save batch to database
                    logging.info(f"💾 Saving batch {batch_num + 1} to database...")
                    save_success = db.save_batch_ticker_data(batch_data)
                    
                    if save_success:
                        logging.info(f"✅ Batch {batch_num + 1} saved to database successfully")
                        successful_batches += 1
                        all_results.extend(batch_data)
                        
                        # Update ticker information in tickers table
                        logging.info(f"📝 Updating ticker information for batch {batch_num + 1}...")
                        for ticker_data in batch_data:
                            ticker = ticker_data['ticker']
                            data = ticker_data['data']
                            
                            # Add/update ticker in tickers table
                            db.add_ticker(
                                ticker_symbol=ticker,
                                company_name=data.get('long_name') or data.get('short_name'),
                                exchange=data.get('exchange'),
                                industry=data.get('industry'),
                                sector=data.get('sector'),
                                country=data.get('country')
                            )
                            
                            # Update last scraped timestamp if method exists
                            try:
                                db.update_ticker_last_scraped(ticker)
                            except AttributeError:
                                logging.debug(f"update_ticker_last_scraped method not available")
                        
                        logging.info(f"✅ Ticker information updated for batch {batch_num + 1}")
                        
                    else:
                        logging.error(f"❌ Failed to save batch {batch_num + 1} to database")
                        failed_batches += 1
                else:
                    logging.warning(f"⚠️ No data fetched for batch {batch_num + 1}")
                    failed_batches += 1
                
            except Exception as e:
                logging.error(f"❌ Error processing batch {batch_num + 1}: {e}")
                failed_batches += 1
                continue
            
            # Batch processing time
            batch_time = time.time() - batch_start_time
            logging.info(f"⏱️ Batch {batch_num + 1} completed in {batch_time:.2f} seconds")
            
            # Add small delay between batches to be respectful to the API
            if batch_num < total_batches - 1:  # Don't delay after the last batch
                delay = 2  # 2 second delay between batches
                logging.info(f"⏳ Waiting {delay} seconds before next batch...")
                time.sleep(delay)
        
        # Final summary
        total_time = time.time() - start_time
        logging.info("=" * 60)
        logging.info("📊 FINAL SUMMARY")
        logging.info("=" * 60)
        logging.info(f"Total tickers processed: {len(tickers)}")
        logging.info(f"Total batches: {total_batches}")
        logging.info(f"Successful batches: {successful_batches}")
        logging.info(f"Failed batches: {failed_batches}")
        logging.info(f"Total data records: {len(all_results)}")
        logging.info(f"Total processing time: {total_time:.2f} seconds")
        logging.info(f"Average time per batch: {total_time/total_batches:.2f} seconds")
        logging.info(f"Success rate: {(successful_batches/total_batches)*100:.1f}%")
        
        if all_results:
            # Save results to JSON file for inspection
            import json
            output_filename = f"test_first_100_tickers_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_filename, 'w') as f:
                json.dump(all_results, f, indent=2, default=str)
            logging.info(f"💾 Results saved to {output_filename}")
        
        logging.info("=" * 60)
        
    except Exception as e:
        logging.error(f"❌ Fatal error in main: {e}")
        raise
    finally:
        # Close database connection
        if 'db' in locals():
            db.close_connection()
            logging.info("🔌 Database connection closed")

if __name__ == "__main__":
    main()
