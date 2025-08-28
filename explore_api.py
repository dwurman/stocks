#!/usr/bin/env python3
"""
Explore yfinance API and save detailed results
"""

from debug_yfinance import *

def main():
    print('Detailed exploration...')
    categories = explore_info_categories('AAPL')
    
    print('\nHistorical data...')
    hist = explore_historical_data('AAPL', '1mo')
    
    print('\nFinancial data...')
    explore_financials('AAPL')
    
    print('\nSaving sample data...')
    save_sample_data('AAPL')
    
    print('\nAPI call debugging...')
    debug_api_calls()

if __name__ == "__main__":
    main()

