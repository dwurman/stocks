#!/usr/bin/env python3
"""
Simplified Database Manager for Yahoo Finance Data
Uses a single table to store all ticker data
"""

import os
import logging
import psycopg2
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self, fallback_mode=False):
        """Initialize PostgreSQL database connection"""
        self.fallback_mode = fallback_mode
        
        if fallback_mode:
            logging.warning("Running in FALLBACK MODE - no database operations will be performed")
            self.connection = None
            return
        
        # Get PostgreSQL connection details from environment
        self.db_url = os.getenv('NHOST_URL')  # This should be your PostgreSQL connection string
        self.db_password = os.getenv('NHOST_ADMIN_SECRET')  # This should be your database password
        
        if not self.db_url or not self.db_password:
            logging.warning("NHOST_URL (PostgreSQL URL) or NHOST_ADMIN_SECRET (database password) not found, switching to fallback mode")
            self.fallback_mode = True
            self.connection = None
            return
        
        try:
            # Parse the connection string and add password
            if self.db_url.startswith('postgresql://') or self.db_url.startswith('postgres://'):
                # If it's already a full connection string, just add password
                if 'password=' not in self.db_url:
                    self.db_url = self.db_url.replace('postgresql://', f'postgresql://:{self.db_password}@')
            else:
                # If it's just the host, construct the full connection string
                # Use the exact format: postgres://postgres:[PASSWORD]@[HOST]:5432/[DATABASE_NAME]
                import urllib.parse
                encoded_password = urllib.parse.quote_plus(self.db_password)
                # Extract database name from host (everything before .db.us-east-1.nhost.run)
                db_name = self.db_url.split('.')[0]
                self.db_url = f"postgres://postgres:{encoded_password}@{self.db_url}:5432/{db_name}"
            
            # Test connection
            self._test_connection()
            
            # Ensure the table exists
            self._create_table_if_not_exists()
            
            logging.info("PostgreSQL database connection established successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize PostgreSQL connection: {str(e)}")
            logging.warning("Switching to fallback mode")
            self.fallback_mode = True
            self.connection = None
    
    def _test_connection(self):
        """Test the database connection"""
        try:
            # Try connection string first
            try:
                self.connection = psycopg2.connect(self.db_url)
            except Exception as e:
                logging.warning(f"Connection string failed, trying individual parameters: {str(e)}")
                # Fallback to individual parameters
                import urllib.parse
                if self.db_url.startswith('postgresql://'):
                    # Parse the connection string
                    from urllib.parse import urlparse
                    parsed = urlparse(self.db_url)
                    host = parsed.hostname
                    port = parsed.port or 5432
                    database = parsed.path[1:] if parsed.path else 'postgres'
                else:
                    # Use the host directly
                    host = self.db_url
                    port = 5432
                    database = 'postgres'
                
                # Try different username combinations that Nhost commonly uses
                self.connection = self._try_different_users(host, port, database)
            
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                logging.info(f"Connected to PostgreSQL: {version[0]}")
            
        except Exception as e:
            logging.error(f"PostgreSQL connection test failed: {str(e)}")
            raise
    
    def _try_different_users(self, host, port, database):
        """Try different username combinations for Nhost PostgreSQL"""
        # Common username combinations for Nhost
        user_combinations = [
            ('postgres', self.db_password),
            ('nhost', self.db_password),
            ('admin', self.db_password),
        ]
        
        for username, password in user_combinations:
            try:
                logging.info(f"Trying username: {username}")
                connection = psycopg2.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=username,
                    password=password
                )
                logging.info(f"Successfully connected with username: {username}")
                return connection
            except Exception as e:
                logging.warning(f"Failed with username {username}: {str(e)}")
                continue
        
        raise Exception("Failed to connect with any username combination")
    
    def _create_table_if_not_exists(self):
        """Create the ticker_data table if it doesn't exist"""
        if self.fallback_mode:
            logging.info("FALLBACK MODE: Would create ticker_data table")
            return
        
        try:
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS ticker_data (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(20) NOT NULL,
                scraped_at TIMESTAMPTZ NOT NULL,
                
                -- Essential fields as separate columns for easy querying
                long_name VARCHAR(255),
                sector VARCHAR(100),
                industry VARCHAR(100),
                current_price DECIMAL(15,4),
                market_cap NUMERIC(25,2),
                volume BIGINT,
                exchange VARCHAR(20),
                
                -- All other data stored as JSON for flexibility
                data_json JSONB
            );
            """
            
            # Create table first
            with self.connection.cursor() as cursor:
                cursor.execute(create_table_sql)
                self.connection.commit()
                logging.info("Table creation completed successfully")
            
            # Skip index creation for now - just create the table
            logging.info("Table created successfully - indexes can be added later")
                
        except Exception as e:
            logging.error(f"Failed to create table: {str(e)}")
            raise
    
    def save_ticker_data(self, ticker_data: Dict[str, Any]) -> bool:
        """Save a single ticker's data to the database"""
        if self.fallback_mode:
            logging.info(f"FALLBACK MODE: Would save ticker data for {ticker_data.get('ticker', 'UNKNOWN')}")
            return True
        
        try:
            ticker = ticker_data['ticker']
            scraped_at = ticker_data['scraped_at']
            data = ticker_data['data']
            
            # Check if we already have data for this ticker today
            existing = self.get_ticker_data_for_date(ticker, scraped_at.date())
            if existing:
                logging.info(f"Data for {ticker} on {scraped_at.date()} already exists, skipping")
                return True
            
            # Prepare the insert statement
            insert_sql = """
            INSERT INTO ticker_data (
                ticker, scraped_at, long_name, sector, industry, current_price, market_cap, volume, exchange, data_json
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            # Extract values from data dictionary, handling missing keys gracefully
            values = (
                ticker, scraped_at,
                data.get('long_name'), data.get('sector'), data.get('industry'),
                data.get('current_price'), data.get('market_cap'), data.get('volume'),
                data.get('exchange'), json.dumps(data) # Store all data as JSON
            )
            
            with self.connection.cursor() as cursor:
                cursor.execute(insert_sql, values)
                self.connection.commit()
                logging.info(f"Successfully saved data for {ticker}")
                return True
                
        except Exception as e:
            logging.error(f"Failed to save ticker data for {ticker_data.get('ticker', 'UNKNOWN')}: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def save_batch_ticker_data(self, ticker_data_list: List[Dict[str, Any]]) -> bool:
        """Save multiple tickers' data to the database"""
        if self.fallback_mode:
            logging.info(f"FALLBACK MODE: Would save batch of {len(ticker_data_list)} tickers to database")
            return True
        
        if not ticker_data_list:
            logging.warning("No ticker data provided for batch save")
            return False
        
        try:
            logging.info(f"🚀 Starting optimized bulk save for {len(ticker_data_list)} tickers...")
            
            # Check existing records for today
            tickers = [td['ticker'] for td in ticker_data_list]
            today = datetime.now().date()
            existing_tickers = self.get_tickers_with_data_today(tickers)
            
            # Filter out tickers that already have data today
            new_tickers = [td for td in ticker_data_list if td['ticker'] not in existing_tickers]
            existing_tickers_to_update = [td for td in ticker_data_list if td['ticker'] in existing_tickers]
            
            logging.info(f"📊 Found {len(new_tickers)} new records and {len(existing_tickers_to_update)} existing records to update")
            
            success_count = 0
            
            # Save new records
            if new_tickers:
                logging.info(f"💾 Attempting bulk insert for {len(new_tickers)} new records...")
                for ticker_data in new_tickers:
                    if self.save_ticker_data(ticker_data):
                        success_count += 1
                    else:
                        logging.error(f"Failed to save {ticker_data.get('ticker', 'UNKNOWN')}")
            
            # For now, we'll skip updates (you can implement this later if needed)
            if existing_tickers_to_update:
                logging.info(f"⏭️ Skipping {len(existing_tickers_to_update)} existing records (update not implemented)")
            
            logging.info(f"✅ Successfully bulk inserted {success_count} new ticker records")
            return success_count == len(new_tickers)
            
        except Exception as e:
            logging.error(f"Failed to save batch ticker data: {str(e)}")
            return False
    
    def get_ticker_data_for_date(self, ticker: str, date: datetime.date) -> Optional[Dict[str, Any]]:
        """Get ticker data for a specific date"""
        if self.fallback_mode:
            logging.info(f"FALLBACK MODE: Would get ticker data for {ticker} on {date}")
            return None
        
        try:
            query = """
            SELECT * FROM ticker_data 
            WHERE ticker = %s AND DATE(scraped_at) = %s 
            ORDER BY scraped_at DESC 
            LIMIT 1
            """
            
            with self.connection.cursor() as cursor:
                cursor.execute(query, (ticker, date))
                result = cursor.fetchone()
                
                if result:
                    # Convert to dictionary
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, result))
                return None
                
        except Exception as e:
            logging.error(f"Failed to get ticker data for {ticker} on {date}: {str(e)}")
            return None
    
    def get_tickers_with_data_today(self, tickers: List[str]) -> Set[str]:
        """Get list of tickers that already have data for today"""
        if self.fallback_mode:
            logging.info("FALLBACK MODE: Would get tickers with data today")
            return set()
        
        try:
            today = datetime.now().date()
            placeholders = ','.join(['%s'] * len(tickers))
            query = f"""
            SELECT DISTINCT ticker FROM ticker_data 
            WHERE ticker IN ({placeholders}) AND DATE(scraped_at) = %s
            """
            
            with self.connection.cursor() as cursor:
                cursor.execute(query, tickers + [today])
                results = cursor.fetchall()
                return {row[0] for row in results}
                
        except Exception as e:
            logging.error(f"Failed to get tickers with data today: {str(e)}")
            return set()
    
    def close_connection(self):
        """Close the database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()
            logging.info("Database connection closed")
