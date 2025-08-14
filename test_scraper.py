import json
import os
from scraper import YahooFinanceScraper

def load_stocks_from_file(filename='stocks.txt'):
    """Load stock tickers from the specified file"""
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        return []
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return []

def build_yahoo_finance_url(ticker):
    """Build Yahoo Finance analysis URL for a given ticker"""
    base_url = "https://finance.yahoo.com/quote/{}/analysis/"
    return base_url.format(ticker)

def test_scraper_with_all_tickers():
    """Test the scraper with all tickers from stocks.txt"""
    print("🚀 Starting Yahoo Finance Scraper Test")
    print("=" * 60)
    
    # Load all tickers from stocks.txt
    tickers = load_stocks_from_file()
    if not tickers:
        print("❌ No tickers loaded. Exiting.")
        return
    
    print(f"📊 Loaded {len(tickers)} tickers: {', '.join(tickers)}")
    print()
    
    # Initialize the scraper
    try:
        scraper = YahooFinanceScraper()
        print("✅ Scraper initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize scraper: {e}")
        return
    
    print()
    
    # Process each ticker
    for i, ticker in enumerate(tickers, 1):
        print(f"🔄 Processing ticker {i}/{len(tickers)}: {ticker}")
        print("-" * 40)
        
        try:
            # Build the URL for this ticker
            url = build_yahoo_finance_url(ticker)
            print(f"🌐 URL: {url}")
            
            # Scrape the website
            print("📥 Scraping website...")
            html_content = scraper.scrape_website(ticker)
            
            if html_content:
                print("✅ Website scraped successfully")
                
                # Parse the content
                print("�� Parsing content...")
                ticker_data = scraper.parse_yahoo_finance_content(html_content, ticker)
                
                if ticker_data:
                    print("✅ Content parsed successfully")
                    
                    # Output the JSON data
                    print("�� Extracted Data:")
                    print(json.dumps(ticker_data, indent=2))
                    
                    # Summary of what was extracted
                    data_keys = list(ticker_data.get('data', {}).keys())
                    print(f"\n�� Data Summary: {len(data_keys)} data categories extracted")
                    if data_keys:
                        print(f"   Categories: {', '.join(data_keys)}")
                    
                else:
                    print("❌ Failed to parse content")
                    print("   Raw HTML length:", len(html_content))
                    
            else:
                print("❌ Failed to scrape website")
                
        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")
        
        print()
        
        # Add a small delay between requests to be respectful
        if i < len(tickers):
            print("⏳ Waiting 2 seconds before next request...")
            import time
            time.sleep(2)
            print()
    
    print("=" * 60)
    print("🎉 Scraper test completed!")
    print(f"📈 Processed {len(tickers)} tickers")

def test_scraper_with_single_ticker(ticker='AAPL'):
    """Test the scraper with a single ticker (for debugging)"""
    print(f"🧪 Testing scraper with single ticker: {ticker}")
    print("=" * 40)
    
    try:
        scraper = YahooFinanceScraper()
        url = build_yahoo_finance_url(ticker)
        
        print(f"🌐 URL: {url}")
        print("📥 Scraping...")
        
        html_content = scraper.scrape_website(ticker)
        if html_content:
            print("✅ Scraped successfully")
            ticker_data = scraper.parse_yahoo_finance_content(html_content, ticker)
            if ticker_data:
                print("✅ Parsed successfully")
                print("\n📋 Data:")
                print(json.dumps(ticker_data, indent=2))
            else:
                print("❌ Parse failed")
        else:
            print("❌ Scrape failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Check if we want to test a single ticker or all tickers
    import sys
    
    if len(sys.argv) > 1:
        # Test with specific ticker
        ticker = sys.argv[1].upper()
        test_scraper_with_single_ticker(ticker)
    else:
        # Test with all tickers from stocks.txt
        test_scraper_with_all_tickers()