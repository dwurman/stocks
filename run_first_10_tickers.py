#!/usr/bin/env python3
"""
Script to run the scraper for the first 10 tickers from all_tickers_api.txt
and save the data to the database
"""

import logging
from yfinance_api_scraper import YahooFinanceAPIScraper
from db_module import DatabaseManager

def read_first_n_tickers(filename, n=10):
    """Read the first n tickers from the file"""
    tickers = []
    try:
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                if i >= n:
                    break
                ticker = line.strip()
                if ticker:  # Skip empty lines
                    tickers.append(ticker)
        return tickers
    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found")
        return []
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return []

def main():
    """Main function to scrape first 10 tickers and save to database"""
    try:
        # Read first 10 tickers from the file
        tickers = read_first_n_tickers('all_tickers_api.txt', 10)
        
        if not tickers:
            print("❌ No tickers found to process")
            return
        
        print(f"🚀 Starting Yahoo Finance API scraper for first 10 tickers...")
        print(f"📊 Tickers to process: {', '.join(tickers)}")
        
        # Initialize the scraper and database
        scraper = YahooFinanceAPIScraper()
        db = DatabaseManager()
        
        # Scrape data in batches (use batch size of 5 for better performance)
        print(f"\n🔄 Fetching data for {len(tickers)} tickers in batches...")
        batch_data = scraper.get_batch_tickers_info(tickers, batch_size=5)
        
        if batch_data:
            print(f"✅ Successfully fetched data for {len(batch_data)} tickers")
            
            # Save to database
            print("\n💾 Saving data to database...")
            success = db.save_batch_ticker_data(batch_data)
            
            if success:
                print("✅ Data successfully saved to scraped_data table!")
                
                # Update ticker information in tickers table
                print("\n📝 Updating ticker information in tickers table...")
                success_count = 0
                for ticker_data in batch_data:
                    ticker = ticker_data['ticker']
                    data = ticker_data['data']
                    
                    # Add/update ticker in tickers table
                    ticker_id = db.add_ticker(
                        ticker_symbol=ticker,
                        company_name=data.get('company_name'),
                        exchange=data.get('exchange'),
                        industry=data.get('industry'),
                        sector=data.get('sector'),
                        country=data.get('country')
                    )
                    
                    if ticker_id:
                        # Update last scraped timestamp
                        db.update_ticker_last_scraped(ticker)
                        success_count += 1
                
                print(f"✅ Updated ticker information for {success_count}/{len(batch_data)} tickers")
                
                # Display summary
                print(f"\n📊 SUMMARY:")
                print(f"   Tickers processed: {len(batch_data)}")
                print(f"   Data saved to scraped_data table: ✅")
                print(f"   Ticker metadata updated: {success_count}")
                
                # Show some sample data
                print(f"\n📈 Sample data:")
                for i, ticker_data in enumerate(batch_data[:3]):  # Show first 3
                    ticker = ticker_data['ticker']
                    data = ticker_data['data']
                    print(f"   {ticker}: {data.get('company_name', 'N/A')} - ${data.get('current_price', 'N/A')}")
                
                if len(batch_data) > 3:
                    print(f"   ... and {len(batch_data) - 3} more tickers")
                
            else:
                print("❌ Failed to save data to database")
        else:
            print("❌ No data was fetched")
            
    except Exception as e:
        logging.error(f"Error in main: {e}")
        print(f"❌ Error: {e}")
    finally:
        # Close database connection
        if 'db' in locals():
            db.close_connection()

if __name__ == "__main__":
    main()

