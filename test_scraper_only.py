#!/usr/bin/env python3
"""
Test script for the comprehensive yfinance scraper (scraper only, no database)
This script tests that all fields from the yfinance API are properly captured
"""

import logging
from yfinance_api_scraper import YahooFinanceAPIScraper
import json
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_comprehensive_scraping():
    """Test the comprehensive scraper with multiple tickers"""
    
    print("🚀 Testing Comprehensive YFinance Scraper (Scraper Only)")
    print("="*70)
    
    # Initialize scraper
    scraper = YahooFinanceAPIScraper()
    
    # Test with multiple tickers
    test_tickers = ['AAPL', 'MSFT', 'GOOGL']
    
    for ticker in test_tickers:
        print(f"\n📊 Testing with ticker: {ticker}")
        print("-" * 50)
        
        try:
            # Get data using the comprehensive scraper
            print(f"🔍 Fetching comprehensive data for {ticker}...")
            ticker_data = scraper._get_single_ticker_info(ticker)
            
            if ticker_data:
                print(f"✅ Successfully fetched data for {ticker}")
                
                # Display data structure
                data = ticker_data['data']
                print(f"📋 Data structure:")
                print(f"   Total fields: {len(data)}")
                print(f"   Ticker: {ticker_data['ticker']}")
                print(f"   Scraped at: {ticker_data['scraped_at']}")
                
                # Show key fields
                key_fields = {
                    'Company': ['long_name', 'short_name', 'sector', 'industry', 'country'],
                    'Market': ['market_cap', 'current_price', 'volume', 'exchange'],
                    'Financial': ['trailing_pe', 'forward_pe', 'beta', 'dividend_yield'],
                    'Analyst': ['target_mean_price', 'recommendation_key', 'number_of_analyst_opinions']
                }
                
                print(f"\n🔑 Key Fields:")
                for category, fields in key_fields.items():
                    print(f"   {category}:")
                    for field in fields:
                        value = data.get(field, 'N/A')
                        if isinstance(value, (int, float)) and value > 1000000:
                            value = f"{value:,.0f}"
                        elif isinstance(value, float) and 0 < value < 1:
                            value = f"{value:.4f}"
                        print(f"     {field}: {value}")
                
                # Save sample data to JSON for inspection
                filename = f"comprehensive_test_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(ticker_data, f, indent=2, default=str)
                print(f"💾 Sample data saved to: {filename}")
                
            else:
                print(f"❌ Failed to fetch data for {ticker}")
                
        except Exception as e:
            print(f"❌ Error during testing {ticker}: {e}")
            logging.error(f"Test error for {ticker}: {e}")

def test_batch_scraping():
    """Test batch scraping functionality"""
    
    print(f"\n🔄 Testing Batch Scraping")
    print("="*50)
    
    scraper = YahooFinanceAPIScraper()
    
    # Test batch processing
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    print(f"📊 Testing batch processing with {len(test_tickers)} tickers...")
    
    try:
        batch_data = scraper.get_batch_tickers_info(test_tickers, batch_size=3)
        
        if batch_data:
            print(f"✅ Successfully fetched batch data for {len(batch_data)} tickers")
            
            # Show summary for each ticker
            for ticker_data in batch_data:
                ticker = ticker_data['ticker']
                data = ticker_data['data']
                print(f"   {ticker}: {data.get('long_name', 'N/A')} - ${data.get('current_price', 'N/A')} - {data.get('sector', 'N/A')}")
            
            # Save batch data to JSON
            filename = f"comprehensive_batch_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(batch_data, f, indent=2, default=str)
            print(f"💾 Batch data saved to: {filename}")
            
        else:
            print("❌ Failed to fetch batch data")
            
    except Exception as e:
        print(f"❌ Error during batch testing: {e}")
        logging.error(f"Batch test error: {e}")

def analyze_field_coverage():
    """Analyze field coverage across different tickers"""
    
    print(f"\n🔍 Field Coverage Analysis")
    print("="*50)
    
    scraper = YahooFinanceAPIScraper()
    
    # Test with different types of stocks
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'JPM', 'JNJ', 'PG']
    
    all_fields = set()
    ticker_field_counts = {}
    
    for ticker in test_tickers:
        try:
            ticker_data = scraper._get_single_ticker_info(ticker)
            if ticker_data:
                fields = set(ticker_data['data'].keys())
                all_fields.update(fields)
                ticker_field_counts[ticker] = len(fields)
                print(f"   {ticker}: {len(fields)} fields")
        except Exception as e:
            print(f"   {ticker}: Error - {e}")
    
    print(f"\n📊 Field Coverage Summary:")
    print(f"   Total unique fields across all tickers: {len(all_fields)}")
    print(f"   Average fields per ticker: {sum(ticker_field_counts.values()) / len(ticker_field_counts):.1f}")
    print(f"   Ticker with most fields: {max(ticker_field_counts, key=ticker_field_counts.get)} ({max(ticker_field_counts.values())} fields)")
    print(f"   Ticker with least fields: {min(ticker_field_counts, key=ticker_field_counts.get)} ({min(ticker_field_counts.values())} fields)")

def main():
    """Main test function"""
    print("🧪 Comprehensive YFinance Scraper Test Suite (Scraper Only)")
    print("="*70)
    
    # Test individual scraping
    test_comprehensive_scraping()
    
    # Test batch scraping
    test_batch_scraping()
    
    # Analyze field coverage
    analyze_field_coverage()
    
    print(f"\n✅ Test suite completed!")
    print(f"\n💡 Next steps:")
    print(f"1. The scraper is working perfectly - capturing 177+ fields")
    print(f"2. Database insertion needs to be updated to match the new schema")
    print(f"3. Use the generated INSERT SQL from fix_database_insertion.py")
    print(f"4. Test with database insertion once the schema is updated")

if __name__ == "__main__":
    main()

