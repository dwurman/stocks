#!/usr/bin/env python3
"""
Test script for the comprehensive yfinance scraper
This script tests that all fields from the yfinance API are properly captured and stored
"""

import logging
from yfinance_api_scraper import YahooFinanceAPIScraper
from db_module import DatabaseManager
import json
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_comprehensive_scraping():
    """Test the comprehensive scraper with a single ticker"""
    
    print("🚀 Testing Comprehensive YFinance Scraper")
    print("="*60)
    
    # Initialize scraper and database
    scraper = YahooFinanceAPIScraper()
    db = DatabaseManager()
    
    # Test with AAPL
    test_ticker = 'AAPL'
    print(f"📊 Testing with ticker: {test_ticker}")
    
    try:
        # Get data using the comprehensive scraper
        print(f"\n🔍 Fetching comprehensive data for {test_ticker}...")
        ticker_data = scraper._get_single_ticker_info(test_ticker)
        
        if ticker_data:
            print(f"✅ Successfully fetched data for {test_ticker}")
            
            # Display data structure
            data = ticker_data['data']
            print(f"\n📋 Data structure:")
            print(f"   Total fields: {len(data)}")
            print(f"   Ticker: {ticker_data['ticker']}")
            print(f"   Scraped at: {ticker_data['scraped_at']}")
            
            # Show field categories
            categories = {
                'Company Info': ['long_name', 'short_name', 'sector', 'industry', 'country', 'website'],
                'Market Data': ['market_cap', 'current_price', 'volume', 'exchange'],
                'Financial Ratios': ['trailing_pe', 'forward_pe', 'price_to_book', 'beta'],
                'Dividend Info': ['dividend_yield', 'dividend_rate', 'payout_ratio'],
                'Analyst Data': ['target_mean_price', 'recommendation_key', 'number_of_analyst_opinions'],
                'Risk Metrics': ['audit_risk', 'board_risk', 'overall_risk'],
                'Trading Info': ['bid', 'ask', 'tradeable', 'market_state']
            }
            
            print(f"\n🔍 Field Categories:")
            for category, fields in categories.items():
                available_fields = [f for f in fields if f in data and data[f] is not None]
                if available_fields:
                    print(f"   {category}: {len(available_fields)}/{len(fields)} fields available")
                    for field in available_fields[:3]:  # Show first 3
                        value = data[field]
                        if isinstance(value, (int, float)) and value > 1000000:
                            value = f"{value:,.0f}"
                        print(f"     {field}: {value}")
                    if len(available_fields) > 3:
                        print(f"     ... and {len(available_fields) - 3} more")
            
            # Test database insertion
            print(f"\n💾 Testing database insertion...")
            success = db.save_batch_ticker_data([ticker_data])
            
            if success:
                print("✅ Data successfully saved to database!")
                
                # Verify data in database
                print(f"\n🔍 Verifying data in database...")
                verify_data_in_db(db, test_ticker)
                
            else:
                print("❌ Failed to save data to database")
                
        else:
            print(f"❌ Failed to fetch data for {test_ticker}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        logging.error(f"Test error: {e}")
        
    finally:
        # Close database connection
        if 'db' in locals():
            db.close_connection()

def verify_data_in_db(db, ticker):
    """Verify that data was properly stored in the database"""
    try:
        # Query the most recent data for this ticker
        query_sql = """
        SELECT 
            ticker,
            long_name,
            sector,
            industry,
            current_price,
            market_cap,
            volume,
            trailing_pe,
            dividend_yield,
            beta,
            exchange,
            scraped_at,
            COUNT(*) as field_count
        FROM scraped_data 
        WHERE ticker = %s
        ORDER BY scraped_at DESC
        LIMIT 1;
        """
        
        with db.connection.cursor() as cursor:
            cursor.execute(query_sql, (ticker,))
            result = cursor.cursor.fetchone()
            
            if result:
                print(f"✅ Data found in database:")
                print(f"   Ticker: {result[0]}")
                print(f"   Company: {result[1]}")
                print(f"   Sector: {result[2]}")
                print(f"   Industry: {result[3]}")
                print(f"   Price: ${result[4]}" if result[4] else "   Price: N/A")
                print(f"   Market Cap: {result[5]:,.0f}" if result[5] else "   Market Cap: N/A")
                print(f"   Volume: {result[6]:,}" if result[6] else "   Volume: N/A")
                print(f"   P/E Ratio: {result[7]}" if result[7] else "   P/E Ratio: N/A")
                print(f"   Dividend Yield: {result[8]:.2%}" if result[8] else "   Dividend Yield: N/A")
                print(f"   Beta: {result[9]}" if result[9] else "   Beta: N/A")
                print(f"   Exchange: {result[10]}" if result[10] else "   Exchange: N/A")
                print(f"   Scraped at: {result[11]}")
                
                # Count total fields in the record
                count_sql = """
                SELECT COUNT(*) as total_fields
                FROM information_schema.columns 
                WHERE table_name = 'scraped_data';
                """
                cursor.execute(count_sql)
                field_count = cursor.fetchone()[0]
                print(f"   Total database fields: {field_count}")
                
            else:
                print("❌ No data found in database")
                
    except Exception as e:
        print(f"❌ Error verifying data: {e}")

def test_field_coverage():
    """Test that all expected fields are covered"""
    print(f"\n🔍 Testing Field Coverage")
    print("="*40)
    
    # Expected fields from the comprehensive schema
    expected_fields = [
        # Company Information
        'long_name', 'short_name', 'long_business_summary', 'website', 'phone',
        'address1', 'city', 'state', 'zip', 'country', 'full_time_employees',
        'industry', 'industry_key', 'industry_disp', 'sector', 'sector_key',
        'sector_disp', 'ir_website', 'language', 'region', 'type_disp',
        'display_name', 'symbol',
        
        # Market Data
        'market_cap', 'enterprise_value', 'current_price', 'regular_market_price',
        'previous_close', 'open', 'day_low', 'day_high', 'regular_market_open',
        'regular_market_day_low', 'regular_market_day_high', 'regular_market_previous_close',
        'regular_market_change', 'regular_market_change_percent', 'regular_market_day_range',
        'regular_market_time', 'regular_market_volume', 'volume', 'average_volume',
        'average_volume_10days', 'average_daily_volume_10_day', 'average_daily_volume_3_month',
        
        # Price Data
        'price_hint', 'fifty_two_week_low', 'fifty_two_week_high',
        'fifty_two_week_low_change', 'fifty_two_week_low_change_percent',
        'fifty_two_week_high_change', 'fifty_two_week_high_change_percent',
        'fifty_two_week_range', 'fifty_two_week_change_percent', 'fifty_day_average',
        'fifty_day_average_change', 'fifty_day_average_change_percent', 'two_hundred_day_average',
        'two_hundred_day_average_change', 'two_hundred_day_average_change_percent', 'sandp_52_week_change',
        
        # Trading Information
        'bid', 'ask', 'bid_size', 'ask_size', 'tradeable', 'triggerable',
        'has_pre_post_market_data', 'pre_market_price', 'pre_market_change',
        'pre_market_change_percent', 'pre_market_time', 'market_state', 'exchange',
        'full_exchange_name', 'quote_source_name', 'exchange_timezone_name',
        'exchange_timezone_short_name', 'gmt_offset_milliseconds', 'market',
        'first_trade_date_milliseconds', 'source_interval', 'exchange_data_delayed_by',
        
        # Financial Ratios
        'trailing_pe', 'forward_pe', 'price_to_book', 'price_to_sales_trailing_12_months',
        'enterprise_to_revenue', 'enterprise_to_ebitda', 'trailing_peg_ratio',
        'price_eps_current_year', 'eps_trailing_twelve_months', 'eps_forward', 'eps_current_year',
        
        # Dividend Information
        'dividend_rate', 'dividend_yield', 'trailing_annual_dividend_rate',
        'trailing_annual_dividend_yield', 'five_year_avg_dividend_yield', 'payout_ratio',
        'last_dividend_value', 'last_dividend_date', 'ex_dividend_date', 'dividend_date',
        
        # Shares Information
        'shares_outstanding', 'float_shares', 'shares_short', 'shares_short_prior_month',
        'shares_short_previous_month_date', 'date_short_interest', 'shares_percent_shares_out',
        'held_percent_insiders', 'held_percent_institutions', 'short_ratio',
        'short_percent_of_float', 'implied_shares_outstanding',
        
        # Financial Metrics
        'beta', 'book_value', 'total_cash', 'total_cash_per_share', 'total_debt',
        'total_revenue', 'net_income_to_common', 'gross_profits', 'ebitda',
        'free_cashflow', 'operating_cashflow', 'revenue_per_share',
        
        # Growth and Margins
        'earnings_growth', 'revenue_growth', 'earnings_quarterly_growth',
        'gross_margins', 'profit_margins', 'operating_margins', 'ebitda_margins',
        
        # Financial Health
        'debt_to_equity', 'return_on_assets', 'return_on_equity', 'quick_ratio', 'current_ratio',
        
        # Analyst Recommendations
        'target_high_price', 'target_low_price', 'target_mean_price', 'target_median_price',
        'recommendation_mean', 'recommendation_key', 'average_analyst_rating', 'number_of_analyst_opinions',
        
        # Risk Metrics
        'audit_risk', 'board_risk', 'compensation_risk', 'share_holder_rights_risk', 'overall_risk',
        
        # Dates and Timestamps
        'governance_epoch_date', 'compensation_as_of_epoch_date', 'last_fiscal_year_end',
        'next_fiscal_year_end', 'most_recent_quarter', 'earnings_timestamp',
        'earnings_timestamp_start', 'earnings_timestamp_end', 'earnings_call_timestamp_start',
        'earnings_call_timestamp_end', 'is_earnings_date_estimate',
        
        # Additional Fields
        'currency', 'financial_currency', 'quote_type', 'message_board_id',
        'corporate_actions', 'executive_team', 'company_officers',
        'custom_price_alert_confidence', 'esg_populated', 'cryptoTradeable', 'max_age',
        'last_split_factor', 'last_split_date', 'ir_website'
    ]
    
    print(f"Expected total fields: {len(expected_fields)}")
    
    # Test with a sample ticker to see what's actually available
    scraper = YahooFinanceAPIScraper()
    sample_data = scraper._get_single_ticker_info('AAPL')
    
    if sample_data:
        actual_fields = list(sample_data['data'].keys())
        print(f"Actual fields captured: {len(actual_fields)}")
        
        # Check coverage
        missing_fields = [f for f in expected_fields if f not in actual_fields]
        extra_fields = [f for f in actual_fields if f not in expected_fields]
        
        if missing_fields:
            print(f"Missing fields: {len(missing_fields)}")
            print(f"   {', '.join(missing_fields[:10])}{'...' if len(missing_fields) > 10 else ''}")
        
        if extra_fields:
            print(f"Extra fields: {len(extra_fields)}")
            print(f"   {', '.join(extra_fields[:10])}{'...' if len(extra_fields) > 10 else ''}")
        
        coverage = (len(expected_fields) - len(missing_fields)) / len(expected_fields) * 100
        print(f"Field coverage: {coverage:.1f}%")
        
        if coverage >= 95:
            print("✅ Excellent field coverage!")
        elif coverage >= 90:
            print("✅ Good field coverage!")
        elif coverage >= 80:
            print("⚠️  Moderate field coverage")
        else:
            print("❌ Poor field coverage")

def main():
    """Main test function"""
    print("🧪 Comprehensive YFinance Scraper Test Suite")
    print("="*60)
    
    # Test field coverage first
    test_field_coverage()
    
    # Test comprehensive scraping
    test_comprehensive_scraping()
    
    print(f"\n✅ Test suite completed!")

if __name__ == "__main__":
    main()
