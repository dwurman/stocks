#!/usr/bin/env python3
"""
Debug script to count fields in the INSERT statement
"""

# Count the fields in the INSERT statement
insert_fields = [
    'ticker', 'scraped_at', 'company_name', 'long_name', 'short_name', 'sector', 'industry', 
    'website', 'business_summary', 'country', 'currency', 'exchange', 'quote_type', 'market_cap', 
    'enterprise_value', 'float_shares', 'shares_outstanding', 'shares_short', 
    'shares_short_prev_month', 'shares_short_prior_month', 'current_price', 'previous_close', 
    'open', 'day_low', 'day_high', 'fifty_two_week_low', 'fifty_two_week_high', 
    'fifty_day_average', 'two_hundred_day_average', 'volume', 'average_volume', 
    'average_volume_10days', 'bid', 'ask', 'bid_size', 'ask_size', 'trailing_pe', 'forward_pe', 
    'peg_ratio', 'price_to_book', 'price_to_sales_trailing_12_months', 'debt_to_equity', 
    'return_on_equity', 'return_on_assets', 'trailing_eps', 'forward_eps', 'dividend_yield', 
    'dividend_rate', 'payout_ratio', 'five_year_avg_dividend_yield', 'revenue_growth', 
    'earnings_growth', 'profit_margins', 'operating_margins', 'ebitda_margins', 'beta', 
    'book_value', 'short_ratio', 'price_target_low', 'price_target_mean', 'price_target_high', 
    'price_target_median', 'regular_market_time', 'regular_market_open', 
    'regular_market_close', 'regular_market_previous_close'
]

print(f"Number of fields: {len(insert_fields)}")

# Manually count the placeholders from the VALUES clause
# Line 1: 20 placeholders
# Line 2: 20 placeholders  
# Line 3: 20 placeholders
# Line 4: 10 placeholders
# Total: 70 placeholders

manual_placeholder_count = 70
print(f"Manual placeholder count: {manual_placeholder_count}")

# Check if they match
if len(insert_fields) == manual_placeholder_count:
    print("✅ Field count matches placeholder count")
else:
    print(f"❌ Mismatch: {len(insert_fields)} fields vs {manual_placeholder_count} placeholders")
    print(f"Difference: {len(insert_fields) - manual_placeholder_count}")

print(f"\nFields list:")
for i, field in enumerate(insert_fields, 1):
    print(f"{i:2d}. {field}")
