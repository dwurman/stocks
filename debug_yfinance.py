#!/usr/bin/env python3
"""
Debug script for exploring the yfinance API
This script provides various functions to explore and debug yfinance functionality
"""

import yfinance as yf
import json
import pprint
from datetime import datetime, timedelta

# Sample tickers for testing
SAMPLE_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']

def explore_single_ticker(ticker='AAPL'):
    """Explore a single ticker in detail"""
    print(f"\n🔍 Exploring ticker: {ticker}")
    print("="*50)
    
    # Create ticker object
    stock = yf.Ticker(ticker)
    
    # Get basic info
    print(f"\n📊 Basic Info (.info):")
    info = stock.info
    print(f"Keys available: {len(info.keys())}")
    print(f"Sample keys: {list(info.keys())[:10]}")
    
    # Key information
    key_fields = ['longName', 'sector', 'industry', 'currentPrice', 'marketCap', 
                  'trailingPE', 'dividendYield', 'fiftyTwoWeekHigh', 'fiftyTwoWeekLow']
    
    print(f"\n🔑 Key Fields:")
    for field in key_fields:
        value = info.get(field, 'N/A')
        print(f"  {field}: {value}")
    
    return stock, info

def explore_batch_tickers(tickers=None):
    """Explore batch ticker functionality"""
    if tickers is None:
        tickers = SAMPLE_TICKERS[:3]  # Use first 3 for testing
    
    print(f"\n🔍 Exploring batch tickers: {tickers}")
    print("="*50)
    
    # Create batch ticker object
    ticker_string = ' '.join(tickers)
    batch_tickers = yf.Tickers(ticker_string)
    
    print(f"Batch ticker object created for: {ticker_string}")
    print(f"Available tickers: {list(batch_tickers.tickers.keys())}")
    
    # Explore each ticker in the batch
    for ticker in tickers:
        print(f"\n📊 {ticker}:")
        try:
            stock = batch_tickers.tickers[ticker]
            info = stock.info
            print(f"  Company: {info.get('longName', 'N/A')}")
            print(f"  Price: ${info.get('currentPrice', 'N/A')}")
            print(f"  Market Cap: {info.get('marketCap', 'N/A')}")
        except Exception as e:
            print(f"  Error: {e}")
    
    return batch_tickers

def explore_historical_data(ticker='AAPL', period='1mo'):
    """Explore historical data functionality"""
    print(f"\n📈 Historical data for {ticker} ({period}):")
    print("="*50)
    
    stock = yf.Ticker(ticker)
    
    # Get historical data
    hist = stock.history(period=period)
    print(f"Historical data shape: {hist.shape}")
    print(f"Columns: {list(hist.columns)}")
    print(f"Date range: {hist.index[0]} to {hist.index[-1]}")
    
    # Show sample data
    print(f"\nSample data (last 5 days):")
    print(hist.tail())
    
    return hist

def explore_financials(ticker='AAPL'):
    """Explore financial statements"""
    print(f"\n💰 Financial data for {ticker}:")
    print("="*50)
    
    stock = yf.Ticker(ticker)
    
    # Try different financial data
    financial_methods = [
        ('financials', 'Income Statement'),
        ('balance_sheet', 'Balance Sheet'), 
        ('cashflow', 'Cash Flow'),
        ('earnings', 'Earnings'),
        ('dividends', 'Dividends'),
        ('splits', 'Stock Splits')
    ]
    
    for method, description in financial_methods:
        try:
            print(f"\n📊 {description} (.{method}):")
            data = getattr(stock, method)
            if hasattr(data, 'shape'):
                print(f"  Shape: {data.shape}")
                if not data.empty:
                    print(f"  Columns: {list(data.columns)[:5]}...")  # First 5 columns
                    print(f"  Index: {list(data.index)[:5]}...")      # First 5 rows
                else:
                    print("  No data available")
            else:
                print(f"  Data type: {type(data)}")
                print(f"  Content: {data}")
        except Exception as e:
            print(f"  Error getting {description}: {e}")

def explore_info_categories(ticker='AAPL'):
    """Categorize and explore all available info fields"""
    print(f"\n🗂️ Info field categories for {ticker}:")
    print("="*50)
    
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # Categorize fields by type and content
    categories = {
        'company_info': [],
        'price_data': [],
        'market_data': [],
        'financial_ratios': [],
        'trading_info': [],
        'dates': [],
        'other': []
    }
    
    # Keywords for categorization
    company_keywords = ['name', 'sector', 'industry', 'country', 'website', 'summary', 'employees']
    price_keywords = ['price', 'close', 'open', 'high', 'low', 'target']
    market_keywords = ['market', 'cap', 'volume', 'shares', 'float']
    ratio_keywords = ['pe', 'ratio', 'yield', 'margin', 'return', 'debt', 'eps']
    trading_keywords = ['bid', 'ask', 'size', 'average']
    date_keywords = ['date', 'time', 'ex']
    
    for key, value in info.items():
        key_lower = key.lower()
        categorized = False
        
        for keyword in company_keywords:
            if keyword in key_lower:
                categories['company_info'].append((key, value))
                categorized = True
                break
        
        if not categorized:
            for keyword in price_keywords:
                if keyword in key_lower:
                    categories['price_data'].append((key, value))
                    categorized = True
                    break
        
        if not categorized:
            for keyword in market_keywords:
                if keyword in key_lower:
                    categories['market_data'].append((key, value))
                    categorized = True
                    break
        
        if not categorized:
            for keyword in ratio_keywords:
                if keyword in key_lower:
                    categories['financial_ratios'].append((key, value))
                    categorized = True
                    break
        
        if not categorized:
            for keyword in trading_keywords:
                if keyword in key_lower:
                    categories['trading_info'].append((key, value))
                    categorized = True
                    break
        
        if not categorized:
            for keyword in date_keywords:
                if keyword in key_lower:
                    categories['dates'].append((key, value))
                    categorized = True
                    break
        
        if not categorized:
            categories['other'].append((key, value))
    
    # Display categories
    for category, items in categories.items():
        if items:
            print(f"\n📋 {category.replace('_', ' ').title()} ({len(items)} fields):")
            for key, value in items[:5]:  # Show first 5 items
                print(f"  {key}: {value}")
            if len(items) > 5:
                print(f"  ... and {len(items) - 5} more")
    
    return categories

def debug_api_calls():
    """Debug different API call patterns"""
    print(f"\n🐛 Debug API call patterns:")
    print("="*50)
    
    ticker = 'AAPL'
    
    # Test different ways to call the API
    print(f"\n1. Direct ticker creation:")
    stock1 = yf.Ticker(ticker)
    print(f"   Ticker object: {stock1}")
    
    print(f"\n2. Batch ticker creation:")
    stocks2 = yf.Tickers(ticker + ' MSFT')
    print(f"   Batch object: {stocks2}")
    print(f"   Individual access: {stocks2.tickers[ticker]}")
    
    print(f"\n3. Quick info access:")
    try:
        quick_info = yf.Ticker(ticker).info
        print(f"   Info keys count: {len(quick_info)}")
        print(f"   Sample fields: {list(quick_info.keys())[:5]}")
    except Exception as e:
        print(f"   Error: {e}")

def save_sample_data(ticker='AAPL', filename=None):
    """Save sample data for analysis"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"yfinance_debug_{ticker}_{timestamp}.json"
    
    print(f"\n💾 Saving sample data to {filename}")
    
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # Create comprehensive sample
    sample_data = {
        'ticker': ticker,
        'timestamp': datetime.now().isoformat(),
        'info': info,
        'info_keys_count': len(info),
        'sample_historical': None,
        'error_log': []
    }
    
    # Try to get historical data
    try:
        hist = stock.history(period='5d')
        sample_data['sample_historical'] = {
            'shape': hist.shape,
            'columns': list(hist.columns),
            'last_close': float(hist['Close'].iloc[-1]) if not hist.empty else None
        }
    except Exception as e:
        sample_data['error_log'].append(f"Historical data error: {str(e)}")
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump(sample_data, f, indent=2, default=str)
    
    print(f"✅ Data saved to {filename}")
    return filename

# Interactive exploration functions
def main_menu():
    """Interactive menu for exploring yfinance"""
    print("\n🚀 YFinance API Explorer")
    print("="*50)
    print("Available functions:")
    print("1. explore_single_ticker('AAPL') - Explore one ticker in detail")
    print("2. explore_batch_tickers(['AAPL', 'MSFT']) - Test batch functionality")
    print("3. explore_historical_data('AAPL') - Get historical data")
    print("4. explore_financials('AAPL') - Financial statements")
    print("5. explore_info_categories('AAPL') - Categorize all info fields")
    print("6. debug_api_calls() - Debug different API patterns")
    print("7. save_sample_data('AAPL') - Save data for analysis")
    print("\nExample usage:")
    print("  stock, info = explore_single_ticker('AAPL')")
    print("  categories = explore_info_categories('MSFT')")
    print("  hist = explore_historical_data('GOOGL', '3mo')")

if __name__ == "__main__":
    # Run some basic exploration
    main_menu()
    
    print(f"\n🔍 Quick exploration with AAPL:")
    stock, info = explore_single_ticker('AAPL')
    
    print(f"\n🔍 Batch test:")
    batch = explore_batch_tickers(['AAPL', 'MSFT'])
    
    # Set up variables for debug console
    # These will be available when you set breakpoints
    sample_ticker = 'AAPL'
    sample_stock = yf.Ticker(sample_ticker)
    sample_info = sample_stock.info
    sample_batch = yf.Tickers('AAPL MSFT GOOGL')
    
    print(f"\n🐛 Debug variables ready:")
    print(f"  sample_ticker = '{sample_ticker}'")
    print(f"  sample_stock = yf.Ticker('{sample_ticker}')")
    print(f"  sample_info = sample_stock.info")
    print(f"  sample_batch = yf.Tickers('AAPL MSFT GOOGL')")
    
    print(f"\n✅ Set a breakpoint here to explore in debug console!")
    # breakpoint()  # Uncomment this line to trigger debugger

