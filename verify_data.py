#!/usr/bin/env python3
"""
Script to verify the data that was saved to the database
"""

import logging
from db_module import DatabaseManager
import psycopg2.extras

def main():
    """Verify data in the database"""
    try:
        db = DatabaseManager()
        
        print("🔍 Verifying data in the database...")
        
        # Query recent data from scraped_data table
        query_sql = """
        SELECT ticker, company_name, current_price, market_cap, sector, exchange, scraped_at
        FROM scraped_data 
        WHERE DATE(scraped_at) = CURRENT_DATE
        ORDER BY scraped_at DESC
        LIMIT 15;
        """
        
        with db.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(query_sql)
            results = cursor.fetchall()
            
            if results:
                print(f"✅ Found {len(results)} records in scraped_data table for today:")
                print("="*80)
                print(f"{'Ticker':<8} {'Company Name':<30} {'Price':<10} {'Market Cap':<15} {'Sector':<20}")
                print("-"*80)
                
                for row in results:
                    ticker = row['ticker']
                    company = (row['company_name'] or 'N/A')[:28]
                    price = f"${row['current_price']}" if row['current_price'] else 'N/A'
                    market_cap = f"{row['market_cap']:,.0f}" if row['market_cap'] else 'N/A'
                    sector = (row['sector'] or 'N/A')[:18]
                    
                    print(f"{ticker:<8} {company:<30} {price:<10} {market_cap:<15} {sector:<20}")
            else:
                print("❌ No data found in scraped_data table for today")
        
        # Query tickers table
        ticker_query_sql = """
        SELECT ticker_symbol, company_name, exchange, sector, industry, last_scraped_at
        FROM tickers 
        WHERE DATE(last_scraped_at) = CURRENT_DATE
        ORDER BY last_scraped_at DESC
        LIMIT 15;
        """
        
        with db.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(ticker_query_sql)
            ticker_results = cursor.fetchall()
            
            if ticker_results:
                print(f"\n✅ Found {len(ticker_results)} records in tickers table updated today:")
                print("="*80)
                print(f"{'Ticker':<8} {'Company Name':<30} {'Exchange':<10} {'Sector':<20}")
                print("-"*80)
                
                for row in ticker_results:
                    ticker = row['ticker_symbol']
                    company = (row['company_name'] or 'N/A')[:28]
                    exchange = (row['exchange'] or 'N/A')[:8]
                    sector = (row['sector'] or 'N/A')[:18]
                    
                    print(f"{ticker:<8} {company:<30} {exchange:<10} {sector:<20}")
            else:
                print("❌ No ticker data found for today")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'db' in locals():
            db.close_connection()

if __name__ == "__main__":
    main()

