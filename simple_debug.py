#!/usr/bin/env python3
"""
Simple debug script for yfinance API exploration
Perfect for setting breakpoints and exploring in debug console
"""

import yfinance as yf
import json
import pprint

# Quick setup for debugging
def setup_debug():
    """Set up common variables for debugging"""
    
    # Single ticker
    ticker = 'AAPL'
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # Batch tickers
    batch = yf.Tickers('AAPL MSFT GOOGL TSLA NVDA')
    
    # Historical data
    hist = stock.history(period='5d')
    
    print(f"🐛 Debug setup complete!")
    print(f"Variables available:")
    print(f"  ticker = '{ticker}'")
    print(f"  stock = yf.Ticker('{ticker}')")
    print(f"  info = stock.info (dict with {len(info)} keys)")
    print(f"  batch = yf.Tickers('AAPL MSFT GOOGL TSLA NVDA')")
    print(f"  hist = stock.history(period='5d') (shape: {hist.shape})")
    
    # Set breakpoint here for debugging
    print(f"\n🔍 Set breakpoint on next line to start exploring...")
    
    # This is where you can set your breakpoint
    debug_point = True  # <-- SET BREAKPOINT HERE
    
    return {
        'ticker': ticker,
        'stock': stock,
        'info': info,
        'batch': batch,
        'hist': hist
    }

def explore_info_keys(info_dict):
    """Helper to explore info dictionary keys"""
    print(f"Total keys: {len(info_dict)}")
    print(f"All keys: {list(info_dict.keys())}")
    return list(info_dict.keys())

def pretty_print_info(info_dict, keys=None):
    """Pretty print specific info keys"""
    if keys is None:
        keys = ['longName', 'currentPrice', 'marketCap', 'sector', 'industry']
    
    for key in keys:
        print(f"{key}: {info_dict.get(key, 'N/A')}")

def explore_batch_access(batch_obj):
    """Explore batch ticker access patterns"""
    print(f"Available tickers: {list(batch_obj.tickers.keys())}")
    
    for ticker_symbol in list(batch_obj.tickers.keys())[:3]:  # First 3
        ticker_obj = batch_obj.tickers[ticker_symbol]
        info = ticker_obj.info
        print(f"{ticker_symbol}: {info.get('longName', 'N/A')} - ${info.get('currentPrice', 'N/A')}")

# Common debug patterns to try in console:
DEBUG_EXAMPLES = """
# Once you hit the breakpoint, try these in the debug console:

# 1. Explore basic info
info['longName']
info['currentPrice'] 
info['marketCap']

# 2. See all available keys
len(info)
list(info.keys())[:10]  # First 10 keys

# 3. Search for specific data
[k for k in info.keys() if 'price' in k.lower()]
[k for k in info.keys() if 'volume' in k.lower()]
[k for k in info.keys() if 'ratio' in k.lower()]

# 4. Batch access
batch.tickers['AAPL'].info['longName']
batch.tickers['MSFT'].info['currentPrice']

# 5. Historical data
hist.head()
hist.tail()
hist['Close'].mean()

# 6. Try different tickers
new_stock = yf.Ticker('GOOGL')
new_info = new_stock.info
new_info['longName']

# 7. Explore financial data (may take time to load)
stock.financials
stock.balance_sheet
stock.earnings

# 8. Get recommendation data
stock.recommendations
stock.calendar

# 9. Explore different time periods
stock.history(period='1y').shape
stock.history(period='1mo').shape
"""

if __name__ == "__main__":
    print("🚀 Starting simple yfinance debug session...")
    
    # Run setup
    debug_vars = setup_debug()
    
    # Print debug examples
    print(DEBUG_EXAMPLES)
    
    print("✅ Ready for debugging!")
    print("💡 Set a breakpoint in setup_debug() function and explore the variables!")

