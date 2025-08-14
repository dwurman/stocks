#!/usr/bin/env python3
"""
Fix data type issues by converting "N/A" values to NULL for numeric fields
"""

def clean_numeric_value(value):
    """Convert "N/A" or invalid numeric values to None (NULL)"""
    if value is None:
        return None
    
    # Convert to string for checking
    str_value = str(value).strip()
    
    # Check for various "N/A" representations
    if str_value in ['N/A', 'n/a', 'NA', 'na', '', 'nan', 'NaN', 'None', 'null']:
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
        
        # If it's a whole number, return as int
        if float_val.is_integer():
            return int(float_val)
        else:
            return float_val
            
    except (ValueError, TypeError):
        # If conversion fails, return None
        return None

def clean_ticker_data(ticker_data):
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
    
    # Clean the data
    data = ticker_data.get('data', {})
    cleaned_data = {}
    
    for field, value in data.items():
        if field in numeric_fields:
            cleaned_data[field] = clean_numeric_value(value)
        else:
            # For non-numeric fields, just pass through (but clean empty strings)
            if value in ['N/A', 'n/a', 'NA', 'na', '']:
                cleaned_data[field] = None
            else:
                cleaned_data[field] = value
    
    # Update the ticker_data
    ticker_data['data'] = cleaned_data
    return ticker_data

# Test the function
if __name__ == "__main__":
    # Sample test data
    test_data = {
        'ticker': 'AAPL',
        'scraped_at': '2025-08-13',
        'data': {
            'market_cap': 'N/A',
            'current_price': '150.25',
            'volume': '1234567',
            'trailing_pe': '25.5',
            'dividend_yield': '5.2%',
            'company_name': 'Apple Inc.',
            'sector': 'Technology'
        }
    }
    
    print("=== BEFORE CLEANING ===")
    print(test_data)
    
    cleaned = clean_ticker_data(test_data)
    
    print("\n=== AFTER CLEANING ===")
    print(cleaned)
    
    print("\n=== DATA TYPE ANALYSIS ===")
    for field, value in cleaned['data'].items():
        print(f"{field}: {value} (type: {type(value).__name__})")
