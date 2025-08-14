#!/usr/bin/env python3
"""
Count the actual fields in the INSERT statement from db_module.py
"""

# The actual INSERT statement from db_module.py
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
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id;
"""

def count_fields_and_placeholders():
    """Count fields and placeholders in the INSERT statement"""
    
    # Extract fields
    fields_start = insert_sql.find('(') + 1
    fields_end = insert_sql.find(')')
    fields_section = insert_sql[fields_start:fields_end]
    
    # Extract VALUES section
    values_start = insert_sql.find('VALUES (') + 8
    values_end = insert_sql.rfind(')')
    values_section = insert_sql[values_start:values_end]
    
    # Count fields
    fields = [field.strip() for field in fields_section.split(',')]
    field_count = len(fields)
    
    # Count placeholders
    placeholder_count = values_section.count('%s')
    
    print("=== ACTUAL INSERT STATEMENT ANALYSIS ===")
    print()
    print(f"Fields found: {field_count}")
    print(f"Placeholders found: {placeholder_count}")
    print()
    
    if field_count != placeholder_count:
        print(f"❌ MISMATCH: Fields ({field_count}) != Placeholders ({placeholder_count})")
        print(f"   Difference: {placeholder_count - field_count} extra placeholders")
    else:
        print(f"✅ Fields and placeholders match: {field_count}")
    
    print()
    print("=== FIELDS ===")
    for i, field in enumerate(fields, 1):
        print(f"{i:2d}. {field}")
    
    print()
    print("=== VALUES SECTION ===")
    print(values_section)
    
    # Count placeholders per line in VALUES
    values_lines = values_section.split('\n')
    print()
    print("=== PLACEHOLDERS PER LINE ===")
    for i, line in enumerate(values_lines):
        if line.strip():
            count = line.count('%s')
            print(f"Line {i+1}: {count} placeholders - {line.strip()}")

if __name__ == "__main__":
    count_fields_and_placeholders()
