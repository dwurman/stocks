#!/usr/bin/env python3
"""
Script to fetch data using yfinance API and save to database
Simplified to work with Ticker.info data only
"""

import logging
from datetime import datetime
from yfinance_api_scraper import YahooFinanceAPIScraper
from db_module import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class APIToDatabaseBridge:
    def __init__(self, use_database=True):
        """Initialize the bridge between API and database"""
        self.logger = logging.getLogger(__name__)
        self.api_scraper = YahooFinanceAPIScraper()
        
        if use_database:
            try:
                self.db_manager = DatabaseManager()
                self.use_db = True
                self.logger.info("Database connection established")
            except Exception as e:
                self.logger.warning(f"Database connection failed: {e}")
                self.use_db = False
        else:
            self.use_db = False
            self.logger.info("Running in database-less mode")
    
    def fetch_and_save_tickers(self, tickers, save_to_db=True, save_to_file=True, batch_size=10):
        """Fetch ticker data via API and save to database in batches using yfinance batch functionality"""
        try:
            self.logger.info(f"Starting to fetch data for {len(tickers)} tickers in batches of {batch_size}...")
            
            successful_saves = 0
            total_processed = 0
            
            # Process tickers in batches
            for i in range(0, len(tickers), batch_size):
                batch_tickers = tickers[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (len(tickers) + batch_size - 1) // batch_size
                
                self.logger.info(f"Processing batch {batch_num}/{total_batches}: {len(batch_tickers)} tickers")
                
                try:
                    # Fetch data for all tickers in this batch using yfinance batch functionality
                    batch_data = self.api_scraper.get_batch_tickers_info(batch_tickers, batch_size)
                    
                    if not batch_data:
                        self.logger.warning(f"No data fetched for batch {batch_num}")
                        total_processed += len(batch_tickers)
                        continue
                    
                    self.logger.info(f"Successfully fetched data for {len(batch_data)} tickers in batch {batch_num}")
                    
                    # Save entire batch to database at once using bulk insert
                    if save_to_db and self.use_db and batch_data:
                        self.logger.info(f"Saving batch {batch_num} with {len(batch_data)} tickers to database...")
                        batch_success = self.db_manager.save_batch_ticker_data(batch_data)
                        
                        if batch_success:
                            successful_saves += len(batch_data)
                            self.logger.info(f"✅ Successfully saved batch {batch_num} to database")
                        else:
                            self.logger.warning(f"⚠️ Failed to save batch {batch_num} to database")
                    
                    total_processed += len(batch_tickers)
                    self.logger.info(f"Batch {batch_num} completed. Total processed: {total_processed}/{len(tickers)}")
                    
                except Exception as e:
                    self.logger.error(f"Error processing batch {batch_num}: {e}")
                    total_processed += len(batch_tickers)
                    continue
            
            self.logger.info(f"Processing completed. Successfully saved {successful_saves}/{len(tickers)} tickers to database")
            return successful_saves > 0
            
        except Exception as e:
            self.logger.error(f"Error in fetch_and_save: {e}")
            return False
    
    def _save_single_ticker_to_database(self, ticker_data):
        """Save single ticker API data to database"""
        try:
            # Transform API data to match database schema
            db_ticker_data = self._transform_for_database(ticker_data)
            
            if not db_ticker_data:
                return False
            
            # Save to database
            success = self.db_manager.save_ticker_data(db_ticker_data)
            return success
            
        except Exception as e:
            self.logger.error(f"Error saving {ticker_data['ticker']} to database: {e}")
            return False
    
    def _save_batch_to_database(self, ticker_data_list):
        """Save a batch of ticker data to database at once"""
        try:
            if not ticker_data_list:
                return False
            
            self.logger.info(f"Saving batch of {len(ticker_data_list)} tickers to database...")
            
            # Transform all ticker data for database
            db_ticker_data_list = []
            for ticker_data in ticker_data_list:
                db_ticker_data = self._transform_for_database(ticker_data)
                if db_ticker_data:
                    db_ticker_data_list.append(db_ticker_data)
            
            if not db_ticker_data_list:
                self.logger.warning("No valid ticker data to save in batch")
                return False
            
            # Save all tickers in the batch using the existing batch save method
            success = self._save_to_database(db_ticker_data_list)
            
            if success:
                self.logger.info(f"✅ Successfully saved batch of {len(db_ticker_data_list)} tickers to database")
            else:
                self.logger.warning(f"⚠️ Failed to save batch of {len(db_ticker_data_list)} tickers to database")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error saving batch to database: {e}")
            return False
    
    def _save_to_database(self, ticker_data_list):
        """Save API data to database"""
        try:
            self.logger.info("Saving API data to database...")
            
            for ticker_data in ticker_data_list:
                try:
                    # Transform API data to match database schema
                    db_ticker_data = self._transform_for_database(ticker_data)
                    
                    # Save to database
                    success = self.db_manager.save_ticker_data(db_ticker_data)
                    
                    if success:
                        self.logger.info(f"✅ Successfully saved {ticker_data['ticker']} to database")
                    else:
                        self.logger.warning(f"⚠️ Failed to save {ticker_data['ticker']} to database")
                        
                except Exception as e:
                    self.logger.error(f"Error saving {ticker_data['ticker']}: {e}")
                    continue
            
            self.logger.info("Database save operation completed")
            
        except Exception as e:
            self.logger.error(f"Error saving to database: {e}")
    
    def _transform_for_database(self, api_ticker_data):
        """Transform API data to match database schema"""
        try:
            # Extract the data section
            api_data = api_ticker_data.get('data', {})
            
            # Clean the data by converting "N/A" values to NULL for numeric fields
            cleaned_data = self._clean_ticker_data(api_data)
            
            # Create database-compatible structure
            db_ticker_data = {
                'ticker': api_ticker_data['ticker'],
                'scraped_at': api_ticker_data['scraped_at'],
                'data': cleaned_data
            }
            
            return db_ticker_data
            
        except Exception as e:
            self.logger.error(f"Error transforming data for database: {e}")
            return None
    
    def _clean_ticker_data(self, data):
        """Clean ticker data by converting "N/A" values to NULL for numeric fields"""
        
        # List of fields that should be numeric (bigint, decimal, etc.)
        numeric_fields = [
            'market_cap', 'enterprise_value', 'float_shares', 'shares_outstanding',
            'shares_short', 'shares_short_prev_month', 'shares_short_prior_month',
            'current_price', 'previous_close', 'open', 'day_low', 'day_high',
            'fifty_two_week_low', 'fifty_two_week_high', 'fifty_day_average',
            'two_hundred_day_average', 'volume', 'average_volume', 'average_volume_10days',
            'bid', 'ask', 'bid_size', 'ask_size', 'trailing_pe', 'forward_pe',
            'peg_ratio', 'price_to_book', 'price_to_sales_trailing_12_months',
            'debt_to_equity', 'return_on_equity', 'return_on_assets', 'trailing_eps',
            'forward_eps', 'dividend_yield', 'dividend_rate', 'payout_ratio',
            'five_year_avg_dividend_yield', 'revenue_growth', 'earnings_growth',
            'profit_margins', 'operating_margins', 'ebitda_margins', 'beta',
            'book_value', 'short_ratio', 'price_target_low', 'price_target_mean',
            'price_target_high', 'price_target_median', 'regular_market_time',
            'regular_market_open', 'regular_market_close', 'regular_market_previous_close',
            'shares_short_ratio', 'shares_short_ratio_prev_month', 'shares_short_ratio_prior_month'
        ]
        
        cleaned_data = {}
        
        for field, value in data.items():
            if field in numeric_fields:
                cleaned_data[field] = self._clean_numeric_value(value)
            else:
                # For non-numeric fields, just pass through (but clean empty strings)
                if value in ['N/A', 'n/a', 'NA', 'na', '']:
                    cleaned_data[field] = None
                else:
                    cleaned_data[field] = value
        
        return cleaned_data
    
    def _clean_numeric_value(self, value):
        """Convert "N/A" or invalid numeric values to None (NULL)"""
        if value is None:
            return None
        
        # Convert to string for checking
        str_value = str(value).strip()
        
        # Check for various "N/A" representations
        if str_value in ['N/A', 'n/a', 'NA', 'na', '', 'nan', 'NaN', 'None', 'null']:
            return None
        
        # Check for infinite values
        if str_value.lower() in ['inf', '-inf', 'infinity', '-infinity']:
            return None
        
        # Try to convert to float/int
        try:
            # Remove any currency symbols or commas
            cleaned = str_value.replace('$', '').replace(',', '').replace('%', '')
            
            # Check if it's a percentage
            if '%' in str_value:
                # Convert percentage to decimal (e.g., "5.2%" -> 0.052)
                return float(cleaned) / 100
            
            # Try to convert to float first
            float_val = float(cleaned)
            
            # Check for infinite values after conversion
            if not float_val.isfinite():
                return None
            
            # Check for extremely large values that would cause database overflow
            # DECIMAL(10,2) can handle up to 99999999.99
            if abs(float_val) > 99999999.99:
                return None
            
            # If it's a whole number, return as int
            if float_val.is_integer():
                return int(float_val)
            else:
                return float_val
                
        except (ValueError, TypeError):
            # If conversion fails, return None
            return None
    
    def get_tickers_from_file(self, filename='all_tickers_api.txt', count=None, skip_existing=False, hours_window=24):
        """Load ticker list from file in alphabetical order, optionally skipping existing tickers within time window"""
        try:
            with open(filename, 'r') as f:
                all_tickers = [line.strip() for line in f if line.strip()]
            
            # Sort tickers alphabetically
            all_tickers.sort()
            
            if skip_existing and self.use_db:
                # Use the new efficient bulk filtering method
                all_tickers = self.db_manager.get_tickers_without_recent_data(all_tickers, hours=hours_window)
                
                if hours_window == 24:
                    self.logger.info(f"Filtered to {len(all_tickers)} tickers without data in last 24 hours")
                else:
                    self.logger.info(f"Filtered to {len(all_tickers)} tickers without data in last {hours_window} hours")
            
            if count and count > len(all_tickers):
                count = len(all_tickers)
                self.logger.warning(f"Requested {count} tickers but only {len(all_tickers)} available")
            
            # Return all tickers if count is None, otherwise return specified count
            if count is None:
                selected_tickers = all_tickers
            else:
                selected_tickers = all_tickers[:count]
            
            self.logger.info(f"Selected {len(selected_tickers)} tickers from {filename} in alphabetical order")
            return selected_tickers
            
        except FileNotFoundError:
            self.logger.warning(f"File {filename} not found, using default tickers")
            return ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 'BRK-B', 'JPM', 'JNJ']
        except Exception as e:
            self.logger.error(f"Error reading ticker file: {e}")
            return ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 'BRK-B', 'JPM', 'JNJ']

def main():
    """Main function"""
    import sys
    
    try:
        # Parse command line arguments
        filename = 'all_tickers_api.txt'
        count = None
        skip_existing = False
        batch_size = 10
        hours_window = 24
        
        i = 1
        while i < len(sys.argv):
            arg = sys.argv[i]
            
            if arg == '--skip-existing' or arg == '-s':
                skip_existing = True
            elif arg == '--count' or arg == '-c':
                if i + 1 < len(sys.argv):
                    count = int(sys.argv[i + 1])
                    i += 1
            elif arg == '--file' or arg == '-f':
                if i + 1 < len(sys.argv):
                    filename = sys.argv[i + 1]
                    i += 1
            elif arg == '--batch-size' or arg == '-b':
                if i + 1 < len(sys.argv):
                    batch_size = int(sys.argv[i + 1])
                    i += 1
            elif arg == '--hours-window' or arg == '-hw':
                if i + 1 < len(sys.argv):
                    hours_window = int(sys.argv[i + 1])
                    i += 1
            elif arg == '--help' or arg == '-h':
                print("Usage: python api_to_database.py [OPTIONS]")
                print("Options:")
                print("  -f, --file FILENAME     Ticker file to process (default: all_tickers_api.txt)")
                print("  -c, --count NUMBER     Number of tickers to process (default: all)")
                print("  -s, --skip-existing    Skip tickers that already have data for today")
                print("  -b, --batch-size SIZE  Batch size for database saves (default: 10)")
                print("  -hw, --hours-window HOURS  Hours window for filtering (default: 24)")
                print("  -h, --help             Show this help message")
                print("\nExamples:")
                print("  python api_to_database.py                                    # Process all tickers")
                print("  python api_to_database.py -c 100                           # Process first 100 tickers")
                print("  python api_to_database.py -s                               # Process only new tickers for today")
                print("  python api_to_database.py -b 20                            # Process in batches of 20")
                print("  python api_to_database.py -f stocks.txt -c 50 -s -b 15     # Process 50 new tickers in batches of 15")
                print("  python api_to_database.py -s -hw 48                        # Process tickers without data in last 48 hours")
                print("  python api_to_database.py -s -hw 6                         # Process tickers without data in last 6 hours")
                return
            else:
                # Legacy support: first argument as filename, second as count
                if filename == 'all_tickers_api.txt':
                    filename = arg
                elif count is None:
                    try:
                        count = int(arg)
                    except ValueError:
                        pass
            
            i += 1
        
        # Initialize the bridge
        bridge = APIToDatabaseBridge(use_database=True)
        
        # Get ticker list from specified file in alphabetical order
        tickers = bridge.get_tickers_from_file(filename, count, skip_existing, hours_window)
        
        if not tickers:
            print("🎯 No tickers to process!")
            if skip_existing:
                print("All tickers already have data for today.")
            return
        
        print(f"🚀 Starting API to Database bridge...")
        print(f"📊 Processing {len(tickers)} tickers from {filename} in alphabetical order...")
        if skip_existing:
            if hours_window == 24:
                print("🔄 Skipping tickers that already have data for today (last 24 hours)")
            else:
                print(f"🔄 Skipping tickers that already have data in last {hours_window} hours")
        print(f"🎯 First 10 tickers: {', '.join(tickers[:10])}...")
        
        # Fetch and save data
        success = bridge.fetch_and_save_tickers(
            tickers=tickers,
            save_to_db=True,
            save_to_file=False,
            batch_size=batch_size
        )
        
        if success:
            print(f"\n🎉 Successfully processed {len(tickers)} tickers!")
            print("✅ Data saved to database")
        else:
            print("\n❌ Processing failed. Check logs for details.")
            
    except Exception as e:
        logging.error(f"Error in main: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
