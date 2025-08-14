#!/usr/bin/env python3
"""
Debug script to count fields in INSERT statement and compare with values
"""
import re

# The INSERT statement from db_module.py
insert_sql = """
INSERT INTO scraped_data (
    ticker, scraped_at, company_name, long_name, short_name, sector, industry, 
    website, business_summary, country, currency, exchange, quote_type, market_cap, 
    enterprise_value, float_shares, shares_outstanding, shares_short, 
    shares_short_prev_month, shares_short_prior_month, current_price, previous_close, 
    open, day_low, day_high, fifty_two_week_low, fifty_two_week_high, 
    fifty_day_average, two_hundred_day_average, volume, average_volume, 
    average_volume_10days, bid, ask, bid_size, ask_size, trailing_pe, forward_pe, 
    peg_ratio, price_to_book, price_to_sales_trailing_12_months, debt_to_equity, 
    return_on_equity, return_on_assets, trailing_eps, forward_eps, dividend_yield, 
    dividend_rate, payout_ratio, five_year_avg_dividend_yield, revenue_growth, 
    earnings_growth, profit_margins, operating_margins, ebitda_margins, beta, 
    book_value, short_ratio, price_target_low, price_target_mean, price_target_high, 
    price_target_median, regular_market_time, regular_market_open, 
    regular_market_close, regular_market_previous_close, shares_short_ratio, 
    shares_short_ratio_prev_month, shares_short_ratio_prior_month, shares_short_ratio_date
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
) RETURNING id;
"""

# The values tuple from db_module.py
insert_data_template = (
    'ticker', 'scraped_at',
    'company_name', 'long_name', 'short_name',
    'sector', 'industry', 'website',
    'business_summary', 'country', 'currency',
    'exchange', 'quote_type', 'market_cap',
    'enterprise_value', 'float_shares',
    'shares_outstanding', 'shares_short',
    'shares_short_prev_month', 'shares_short_prior_month',
    'current_price', 'previous_close', 'open',
    'day_low', 'day_high', 'fifty_two_week_low',
    'fifty_two_week_high', 'fifty_day_average',
    'two_hundred_day_average', 'volume',
    'average_volume', 'average_volume_10days',
    'bid', 'ask', 'bid_size', 'ask_size',
    'trailing_pe', 'forward_pe', 'peg_ratio',
    'price_to_book', 'price_to_sales_trailing_12_months',
    'debt_to_equity', 'return_on_equity',
    'return_on_assets', 'trailing_eps', 'forward_eps',
    'dividend_yield', 'dividend_rate', 'payout_ratio',
    'five_year_avg_dividend_yield', 'revenue_growth',
    'earnings_growth', 'profit_margins',
    'operating_margins', 'ebitda_margins',
    'beta', 'book_value', 'short_ratio',
    'price_target_low', 'price_target_mean',
    'price_target_high', 'price_target_median',
    'regular_market_time', 'regular_market_open',
    'regular_market_close', 'regular_market_previous_close',
    'shares_short_ratio', 'shares_short_ratio_prev_month',
    'shares_short_ratio_prior_month', 'shares_short_ratio_date'
)

def count_fields_in_sql(sql):
    """Count the number of fields in the INSERT statement"""
    # Extract the field list between parentheses
    field_match = re.search(r'INSERT INTO scraped_data \(([^)]+)\)', sql, re.DOTALL)
    if field_match:
        fields = field_match.group(1)
        # Split by comma and clean up whitespace
        field_list = [field.strip() for field in fields.split(',')]
        return len(field_list)
    return 0

def count_placeholders(sql):
    """Count the number of %s placeholders in the VALUES clause"""
    # Extract the VALUES clause
    values_match = re.search(r'VALUES \(([^)]+)\)', sql, re.DOTALL)
    if values_match:
        values = values_match.group(1)
        # Count %s placeholders
        placeholder_count = values.count('%s')
        return placeholder_count
    return 0

def count_values_in_tuple(tuple_data):
    """Count the number of values in the tuple"""
    return len(tuple_data)

# Analyze the SQL and values
print("=== FIELD COUNT ANALYSIS ===")
print()

# Count fields in INSERT statement
field_count = count_fields_in_sql(insert_sql)
print(f"Fields in INSERT statement: {field_count}")

# Count placeholders in VALUES clause
placeholder_count = count_placeholders(insert_sql)
print(f"Placeholders in VALUES clause: {placeholder_count}")

# Count values in the tuple
values_count = count_values_in_tuple(insert_data_template)
print(f"Values in the tuple: {values_count}")

print()

# Check for mismatches
if field_count != placeholder_count:
    print(f"❌ MISMATCH: Fields ({field_count}) != Placeholders ({placeholder_count})")
else:
    print(f"✅ Fields and placeholders match: {field_count}")

if placeholder_count != values_count:
    print(f"❌ MISMATCH: Placeholders ({placeholder_count}) != Values ({values_count})")
else:
    print(f"✅ Placeholders and values match: {placeholder_count}")

if field_count != values_count:
    print(f"❌ MISMATCH: Fields ({field_count}) != Values ({values_count})")
else:
    print(f"✅ Fields and values match: {field_count}")

print()

# Show the field names for verification
print("=== FIELD NAMES ===")
fields = re.search(r'INSERT INTO scraped_data \(([^)]+)\)', insert_sql, re.DOTALL)
if fields:
    field_list = [field.strip() for field in fields.group(1).split(',')]
    for i, field in enumerate(field_list, 1):
        print(f"{i:2d}. {field}")

print()

# Show the values for verification
print("=== VALUES ===")
for i, value in enumerate(insert_data_template, 1):
    print(f"{i:2d}. {value}")
