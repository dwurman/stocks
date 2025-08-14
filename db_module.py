import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
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
            ('postgres', 'postgres'),  # Standard PostgreSQL
            ('postgres', database),    # Database name as password
            ('admin', self.db_password),  # Admin user
            ('root', self.db_password),   # Root user
            (database, self.db_password), # Database name as username
        ]
        
        last_error = None
        
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
                logging.info(f"✅ Successfully connected with username: {username}")
                return connection
                
            except psycopg2.OperationalError as e:
                last_error = e
                logging.debug(f"Failed with username {username}: {str(e)}")
                continue
            except Exception as e:
                last_error = e
                logging.debug(f"Unexpected error with username {username}: {str(e)}")
                continue
        
        # If all combinations failed, raise the last error
        if last_error:
            raise last_error
        else:
            raise Exception("No valid username/password combination found")
    
    def _create_table_if_not_exists(self):
        """Create the scraped_data table if it doesn't exist"""
        try:
            # Comprehensive table for all Ticker.info data
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS scraped_data (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(10) NOT NULL,
                scraped_at TIMESTAMPTZ NOT NULL,
                
                -- Basic company information
                company_name TEXT,
                long_name TEXT,
                short_name TEXT,
                sector TEXT,
                industry TEXT,
                website TEXT,
                business_summary TEXT,
                country TEXT,
                currency TEXT,
                exchange TEXT,
                quote_type TEXT,
                
                -- Market data
                market_cap NUMERIC(20,2),
                enterprise_value NUMERIC(20,2),
                float_shares BIGINT,
                shares_outstanding BIGINT,
                shares_short BIGINT,
                shares_short_prev_month BIGINT,
                shares_short_prior_month BIGINT,
                
                -- Price data
                current_price DECIMAL(10,2),
                previous_close DECIMAL(10,2),
                open DECIMAL(10,2),
                day_low DECIMAL(10,2),
                day_high DECIMAL(10,2),
                fifty_two_week_low DECIMAL(10,2),
                fifty_two_week_high DECIMAL(10,2),
                fifty_day_average DECIMAL(10,2),
                two_hundred_day_average DECIMAL(10,2),
                
                -- Volume and trading
                volume BIGINT,
                average_volume BIGINT,
                average_volume_10days BIGINT,
                bid DECIMAL(10,2),
                ask DECIMAL(10,2),
                bid_size INTEGER,
                ask_size INTEGER,
                
                -- Financial ratios
                trailing_pe DECIMAL(15,4),
                forward_pe DECIMAL(15,4),
                peg_ratio DECIMAL(15,4),
                price_to_book DECIMAL(15,4),
                price_to_sales_trailing_12_months DECIMAL(15,4),
                debt_to_equity DECIMAL(15,4),
                return_on_equity DECIMAL(15,4),
                return_on_assets DECIMAL(15,4),
                
                -- Earnings and dividends
                trailing_eps DECIMAL(15,4),
                forward_eps DECIMAL(15,4),
                dividend_yield DECIMAL(15,4),
                dividend_rate DECIMAL(15,4),
                payout_ratio DECIMAL(15,4),
                five_year_avg_dividend_yield DECIMAL(15,4),
                
                -- Growth metrics
                revenue_growth DECIMAL(15,4),
                earnings_growth DECIMAL(15,4),
                profit_margins DECIMAL(15,4),
                operating_margins DECIMAL(15,4),
                ebitda_margins DECIMAL(15,4),
                
                -- Additional metrics
                beta DECIMAL(15,4),
                book_value DECIMAL(15,4),
                short_ratio DECIMAL(15,4),
                price_target_low DECIMAL(15,4),
                price_target_mean DECIMAL(15,4),
                price_target_high DECIMAL(15,4),
                price_target_median DECIMAL(15,4),
                
                -- Market status
                regular_market_time BIGINT,
                regular_market_open DECIMAL(10,2),
                regular_market_close DECIMAL(10,2),
                regular_market_previous_close DECIMAL(10,2),
                
                -- Additional short ratio fields
                shares_short_ratio DECIMAL(15,4),
                shares_short_ratio_prev_month DECIMAL(15,4),
                shares_short_ratio_prior_month DECIMAL(15,4),
                shares_short_ratio_date DATE,
                
                -- Timestamps
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            
            -- Create indexes for better performance
            CREATE INDEX IF NOT EXISTS idx_scraped_data_ticker ON scraped_data(ticker);
            CREATE INDEX IF NOT EXISTS idx_scraped_data_scraped_at ON scraped_data(scraped_at);
            CREATE INDEX IF NOT EXISTS idx_scraped_data_sector ON scraped_data(sector);
            CREATE INDEX IF NOT EXISTS idx_scraped_data_market_cap ON scraped_data(market_cap);
            """
            
            with self.connection.cursor() as cursor:
                cursor.execute(create_table_sql)
                self.connection.commit()
            
            logging.info("Table creation/verification completed successfully")
            
        except Exception as e:
            logging.warning(f"Table creation check failed: {str(e)}")
            if self.connection:
                self.connection.rollback()
    
    def save_ticker_data(self, ticker_data):
        """Save scraped data for a single ticker to the database"""
        if self.fallback_mode:
            logging.info(f"FALLBACK MODE: Would save data for {ticker_data.get('ticker', 'unknown')} to database")
            return True  # Return True to indicate "success" in fallback mode
        
        try:
            if not ticker_data or 'ticker' not in ticker_data:
                logging.error("Invalid ticker data provided")
                return False
            
            # Check if data already exists for this ticker today
            existing_id = self._get_existing_record_id(ticker_data['ticker'])
            
            if existing_id:
                logging.info(f"Found existing record for {ticker_data['ticker']} today (ID: {existing_id}), will replace")
                # Update the existing record
                success = self._update_ticker_data(existing_id, ticker_data)
            else:
                logging.info(f"No existing record found for {ticker_data['ticker']} today, creating new record")
                # Insert new record
                success = self._insert_ticker_data(ticker_data)
            
            return success
                
        except Exception as e:
            logging.error(f"Error saving data for {ticker_data.get('ticker', 'unknown')}: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def save_batch_ticker_data(self, ticker_data_list):
        """Save multiple ticker data records to the database in bulk"""
        if self.fallback_mode:
            logging.info(f"FALLBACK MODE: Would save batch of {len(ticker_data_list)} tickers to database")
            return True  # Return True to indicate "success" in fallback mode
        
        if not ticker_data_list:
            logging.warning("No ticker data provided for batch save")
            return False
        
        try:
            logging.info(f"Starting bulk save for {len(ticker_data_list)} tickers...")
            
            # Clean and transform the data for database insertion
            cleaned_ticker_data_list = []
            for ticker_data in ticker_data_list:
                if not ticker_data or 'ticker' not in ticker_data:
                    logging.warning(f"Skipping invalid ticker data: {ticker_data}")
                    continue
                
                # Clean the data by converting "N/A" values to NULL for numeric fields
                cleaned_data = self._clean_ticker_data_for_database(ticker_data)
                if cleaned_data:
                    cleaned_ticker_data_list.append(cleaned_data)
            
            if not cleaned_ticker_data_list:
                logging.warning("No valid ticker data to save after cleaning")
                return False
            
            # Separate tickers into new and existing
            new_tickers = []
            update_tickers = []
            
            for ticker_data in cleaned_ticker_data_list:
                # Check if data already exists for this ticker today
                existing_id = self._get_existing_record_id(ticker_data['ticker'])
                
                if existing_id:
                    update_tickers.append((existing_id, ticker_data))
                else:
                    new_tickers.append(ticker_data)
            
            success_count = 0
            
            # Bulk insert new records
            if new_tickers:
                insert_success = self._bulk_insert_ticker_data(new_tickers)
                if insert_success:
                    success_count += len(new_tickers)
                    logging.info(f"✅ Successfully bulk inserted {len(new_tickers)} new ticker records")
                else:
                    logging.error(f"❌ Failed to bulk insert {len(new_tickers)} new ticker records")
            
            # Update existing records (one by one for now, could be optimized later)
            for record_id, ticker_data in update_tickers:
                try:
                    update_success = self._update_ticker_data(record_id, ticker_data)
                    if update_success:
                        success_count += 1
                    else:
                        logging.warning(f"⚠️ Failed to update {ticker_data['ticker']}")
                except Exception as e:
                    logging.error(f"Error updating {ticker_data['ticker']}: {e}")
                    continue
            
            total_processed = len(ticker_data_list)
            logging.info(f"Bulk save completed: {success_count}/{total_processed} tickers processed successfully")
            
            return success_count > 0
            
        except Exception as e:
            logging.error(f"Error in bulk save: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def _get_existing_record_id(self, ticker):
        """Check if a record already exists for this ticker today"""
        try:
            from datetime import datetime, timezone
            
            # Get today's date in local timezone (not UTC)
            local_today = datetime.now().date()
            
            # Convert to string for SQL comparison
            today_str = local_today.strftime('%Y-%m-%d')
            
            # Use string comparison for date part
            check_sql = """
            SELECT id, scraped_at FROM scraped_data 
            WHERE ticker = %s 
            AND TO_CHAR(scraped_at, 'YYYY-MM-DD') = %s
            LIMIT 1;
            """
            
            with self.connection.cursor() as cursor:
                cursor.execute(check_sql, (ticker, today_str))
                result = cursor.fetchone()
                
                if result:
                    record_id, scraped_at = result
                    logging.info(f"Found existing record for {ticker} today ({today_str}): ID={record_id}, scraped_at={scraped_at}")
                    return record_id
                else:
                    logging.info(f"No existing record found for {ticker} today ({today_str})")
                    return None
                
        except Exception as e:
            logging.error(f"Error checking existing record: {str(e)}")
            return None
    
    def _update_ticker_data(self, record_id, ticker_data):
        """Update existing ticker data record"""
        try:
            # Update the main record with all fields
            update_sql = """
            UPDATE scraped_data 
            SET scraped_at = %s, company_name = %s, long_name = %s, short_name = %s, sector = %s, 
                industry = %s, website = %s, business_summary = %s, country = %s, currency = %s, 
                exchange = %s, quote_type = %s, market_cap = %s, enterprise_value = %s, 
                float_shares = %s, shares_outstanding = %s, shares_short = %s, 
                shares_short_prev_month = %s, shares_short_prior_month = %s, current_price = %s, 
                previous_close = %s, open = %s, day_low = %s, day_high = %s, 
                fifty_two_week_low = %s, fifty_two_week_high = %s, fifty_day_average = %s, 
                two_hundred_day_average = %s, volume = %s, average_volume = %s, 
                average_volume_10days = %s, bid = %s, ask = %s, bid_size = %s, ask_size = %s, 
                trailing_pe = %s, forward_pe = %s, peg_ratio = %s, price_to_book = %s, 
                price_to_sales_trailing_12_months = %s, debt_to_equity = %s, 
                return_on_equity = %s, return_on_assets = %s, trailing_eps = %s, forward_eps = %s, 
                dividend_yield = %s, dividend_rate = %s, payout_ratio = %s, 
                five_year_avg_dividend_yield = %s, revenue_growth = %s, earnings_growth = %s, 
                profit_margins = %s, operating_margins = %s, ebitda_margins = %s, beta = %s, 
                book_value = %s, short_ratio = %s, price_target_low = %s, price_target_mean = %s, 
                price_target_high = %s, price_target_median = %s, regular_market_time = %s, 
                regular_market_open = %s, regular_market_close = %s, 
                regular_market_previous_close = %s, shares_short_ratio = %s, 
                shares_short_ratio_prev_month = %s, shares_short_ratio_prior_month = %s, 
                shares_short_ratio_date = %s
            WHERE id = %s;
            """
            
            # Extract data from ticker_data
            data = ticker_data.get('data', {})
            
            update_data = (
                ticker_data['scraped_at'],
                data.get('company_name'), data.get('long_name'), data.get('short_name'),
                data.get('sector'), data.get('industry'), data.get('website'),
                data.get('business_summary'), data.get('country'), data.get('currency'),
                data.get('exchange'), data.get('quote_type'), data.get('market_cap'),
                data.get('enterprise_value'), data.get('float_shares'),
                data.get('shares_outstanding'), data.get('shares_short'),
                data.get('shares_short_prev_month'), data.get('shares_short_prior_month'),
                data.get('current_price'), data.get('previous_close'), data.get('open'),
                data.get('day_low'), data.get('day_high'), data.get('fifty_two_week_low'),
                data.get('fifty_two_week_high'), data.get('fifty_day_average'),
                data.get('two_hundred_day_average'), data.get('volume'),
                data.get('average_volume'), data.get('average_volume_10days'),
                data.get('bid'), data.get('ask'), data.get('bid_size'), data.get('ask_size'),
                data.get('trailing_pe'), data.get('forward_pe'), data.get('peg_ratio'),
                data.get('price_to_book'), data.get('price_to_sales_trailing_12_months'),
                data.get('debt_to_equity'), data.get('return_on_equity'),
                data.get('return_on_assets'), data.get('trailing_eps'), data.get('forward_eps'),
                data.get('dividend_yield'), data.get('dividend_rate'), data.get('payout_ratio'),
                data.get('five_year_avg_dividend_yield'), data.get('revenue_growth'),
                data.get('earnings_growth'), data.get('profit_margins'),
                data.get('operating_margins'), data.get('ebitda_margins'),
                data.get('beta'), data.get('book_value'), data.get('short_ratio'),
                data.get('price_target_low'), data.get('price_target_mean'),
                data.get('price_target_high'), data.get('price_target_median'),
                data.get('regular_market_time'), data.get('regular_market_open'),
                data.get('regular_market_close'), data.get('regular_market_previous_close'),
                data.get('shares_short_ratio'), data.get('shares_short_ratio_prev_month'),
                data.get('shares_short_ratio_prior_month'), data.get('shares_short_ratio_date'),
                record_id
            )
            
            with self.connection.cursor() as cursor:
                cursor.execute(update_sql, update_data)
                self.connection.commit()
                logging.info(f"Successfully updated data for {ticker_data['ticker']} (ID: {record_id})")
                return True
                    
        except Exception as e:
            logging.error(f"Error updating ticker data: {str(e)}")
            return False
    
    def _insert_ticker_data(self, ticker_data):
        """Insert new ticker data record"""
        try:
            # Prepare the main data for insertion
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
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id;
            """
            
            # Extract data from ticker_data
            data = ticker_data.get('data', {})
            
            insert_data = (
                ticker_data['ticker'], ticker_data['scraped_at'],
                data.get('company_name'), data.get('long_name'), data.get('short_name'),
                data.get('sector'), data.get('industry'), data.get('website'),
                data.get('business_summary'), data.get('country'), data.get('currency'),
                data.get('exchange'), data.get('quote_type'), data.get('market_cap'),
                data.get('enterprise_value'), data.get('float_shares'),
                data.get('shares_outstanding'), data.get('shares_short'),
                data.get('shares_short_prev_month'), data.get('shares_short_prior_month'),
                data.get('current_price'), data.get('previous_close'), data.get('open'),
                data.get('day_low'), data.get('day_high'), data.get('fifty_two_week_low'),
                data.get('fifty_two_week_high'), data.get('fifty_day_average'),
                data.get('two_hundred_day_average'), data.get('volume'),
                data.get('average_volume'), data.get('average_volume_10days'),
                data.get('bid'), data.get('ask'), data.get('bid_size'), data.get('ask_size'),
                data.get('trailing_pe'), data.get('forward_pe'), data.get('peg_ratio'),
                data.get('price_to_book'), data.get('price_to_sales_trailing_12_months'),
                data.get('debt_to_equity'), data.get('return_on_equity'),
                data.get('return_on_assets'), data.get('trailing_eps'), data.get('forward_eps'),
                data.get('dividend_yield'), data.get('dividend_rate'), data.get('payout_ratio'),
                data.get('five_year_avg_dividend_yield'), data.get('revenue_growth'),
                data.get('earnings_growth'), data.get('profit_margins'),
                data.get('operating_margins'), data.get('ebitda_margins'),
                data.get('beta'), data.get('book_value'), data.get('short_ratio'),
                data.get('price_target_low'), data.get('price_target_mean'),
                data.get('price_target_high'), data.get('price_target_median'),
                data.get('regular_market_time'), data.get('regular_market_open'),
                data.get('regular_market_close'), data.get('regular_market_previous_close'),
                data.get('shares_short_ratio'), data.get('shares_short_ratio_prev_month'),
                data.get('shares_short_ratio_prior_month'), data.get('shares_short_ratio_date')
            )
            
            with self.connection.cursor() as cursor:
                cursor.execute(insert_sql, insert_data)
                result = cursor.fetchone()
                
                if result:
                    scraped_data_id = result[0]
                    logging.info(f"Successfully created new record for {ticker_data['ticker']} (ID: {scraped_data_id})")
                    self.connection.commit()
                    return True
                else:
                    logging.warning(f"No rows affected when creating record for {ticker_data['ticker']}")
                    return False
                    
        except Exception as e:
            logging.error(f"Error inserting ticker data: {str(e)}")
            return False
    
    def _clean_ticker_data_for_database(self, ticker_data):
        """Clean ticker data by converting "N/A" values to NULL for numeric fields"""
        try:
            # Extract the data section
            api_data = ticker_data.get('data', {})
            
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
            
            cleaned_data = {}
            
            for field, value in api_data.items():
                if field in numeric_fields:
                    cleaned_data[field] = self._clean_numeric_value(value)
                else:
                    # For non-numeric fields, just pass through (but clean empty strings)
                    if value in ['N/A', 'n/a', 'NA', 'na', '']:
                        cleaned_data[field] = None
                    else:
                        cleaned_data[field] = value
            
            # Create database-compatible structure
            cleaned_ticker_data = {
                'ticker': ticker_data['ticker'],
                'scraped_at': ticker_data['scraped_at'],
                'data': cleaned_data
            }
            
            return cleaned_ticker_data
            
        except Exception as e:
            logging.error(f"Error cleaning ticker data for database: {e}")
            return None
    
    def _clean_numeric_value(self, value):
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
    
    def _bulk_insert_ticker_data(self, ticker_data_list):
        """Bulk insert multiple ticker data records using executemany"""
        try:
            if not ticker_data_list:
                return False
            
            # Prepare the bulk insert SQL
            bulk_insert_sql = """
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
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            );
            """
            
            # Prepare all the data tuples for bulk insert
            bulk_insert_data = []
            for ticker_data in ticker_data_list:
                data = ticker_data.get('data', {})
                
                insert_data = (
                    ticker_data['ticker'], ticker_data['scraped_at'],
                    data.get('company_name'), data.get('long_name'), data.get('short_name'),
                    data.get('sector'), data.get('industry'), data.get('website'),
                    data.get('business_summary'), data.get('country'), data.get('currency'),
                    data.get('exchange'), data.get('quote_type'), data.get('market_cap'),
                    data.get('enterprise_value'), data.get('float_shares'),
                    data.get('shares_outstanding'), data.get('shares_short'),
                    data.get('shares_short_prev_month'), data.get('shares_short_prior_month'),
                    data.get('current_price'), data.get('previous_close'), data.get('open'),
                    data.get('day_low'), data.get('day_high'), data.get('fifty_two_week_low'),
                    data.get('fifty_two_week_high'), data.get('fifty_day_average'),
                    data.get('two_hundred_day_average'), data.get('volume'),
                    data.get('average_volume'), data.get('average_volume_10days'),
                    data.get('bid'), data.get('ask'), data.get('bid_size'), data.get('ask_size'),
                    data.get('trailing_pe'), data.get('forward_pe'), data.get('peg_ratio'),
                    data.get('price_to_book'), data.get('price_to_sales_trailing_12_months'),
                    data.get('debt_to_equity'), data.get('return_on_equity'),
                    data.get('return_on_assets'), data.get('trailing_eps'), data.get('forward_eps'),
                    data.get('dividend_yield'), data.get('dividend_rate'), data.get('payout_ratio'),
                    data.get('five_year_avg_dividend_yield'), data.get('revenue_growth'),
                    data.get('earnings_growth'), data.get('profit_margins'),
                    data.get('operating_margins'), data.get('ebitda_margins'),
                    data.get('beta'), data.get('book_value'), data.get('short_ratio'),
                    data.get('price_target_low'), data.get('price_target_mean'),
                    data.get('price_target_high'), data.get('price_target_median'),
                    data.get('regular_market_time'), data.get('regular_market_open'),
                    data.get('regular_market_close'), data.get('regular_market_previous_close'),
                    data.get('shares_short_ratio'), data.get('shares_short_ratio_prev_month'),
                    data.get('shares_short_ratio_prior_month'), data.get('shares_short_ratio_date')
                )
                bulk_insert_data.append(insert_data)
            
            # Execute bulk insert
            with self.connection.cursor() as cursor:
                cursor.executemany(bulk_insert_sql, bulk_insert_data)
                affected_rows = cursor.rowcount
                self.connection.commit()
                
                logging.info(f"Successfully bulk inserted {affected_rows} ticker records")
                return True
                    
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error in bulk insert: {error_msg}")
            
            # Check for specific numeric overflow errors
            if "numeric field overflow" in error_msg.lower():
                logging.error("🔴 NUMERIC OVERFLOW ERROR DETECTED!")
                logging.error("This usually means some ticker data contains infinite values or extremely large numbers")
                logging.error("The data cleaning should have caught these, but some may have slipped through")
                
                # Log the problematic data for debugging
                logging.error("Problematic data that may cause overflow:")
                for i, ticker_data in enumerate(ticker_data_list):
                    data = ticker_data.get('data', {})
                    ticker = ticker_data.get('ticker', 'UNKNOWN')
                    
                    # Check for problematic values in numeric fields
                    problematic_fields = []
                    for field, value in data.items():
                        if isinstance(value, (int, float)):
                            if not isinstance(value, bool):  # Skip boolean values
                                if abs(value) > 99999999.99:
                                    problematic_fields.append(f"{field}: {value}")
                                elif not isinstance(value, int) and not value.isfinite():
                                    problematic_fields.append(f"{field}: {value}")
                    
                    if problematic_fields:
                        logging.error(f"  Ticker {ticker} has problematic values: {problematic_fields}")
            
            if self.connection:
                self.connection.rollback()
            return False
    
    def get_ticker_history(self, ticker, limit=10):
        """Retrieve historical data for a specific ticker"""
        if self.fallback_mode:
            logging.info(f"FALLBACK MODE: Would retrieve history for {ticker}")
            return []
        
        try:
            # Get main scraped data
            query_sql = """
            SELECT * FROM scraped_data
            WHERE ticker = %s
            ORDER BY scraped_at DESC
            LIMIT %s;
            """
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query_sql, (ticker, limit))
                results = cursor.fetchall()
                
                # Convert to list of dictionaries
                history = [dict(row) for row in results]
                
                logging.info(f"Retrieved {len(history)} records for {ticker}")
                return history
                
        except Exception as e:
            logging.error(f"Error retrieving history for {ticker}: {str(e)}")
            return []
    
    def cleanup_old_data(self, days_to_keep=30):
        """Clean up old scraped data older than specified days"""
        if self.fallback_mode:
            logging.info(f"FALLBACK MODE: Would cleanup data older than {days_to_keep} days")
            return 0
        
        try:
            cleanup_sql = """
            DELETE FROM scraped_data
            WHERE scraped_at < NOW() - INTERVAL '%s days';
            """
            
            with self.connection.cursor() as cursor:
                cursor.execute(cleanup_sql, (days_to_keep,))
                affected_rows = cursor.rowcount
                self.connection.commit()
                
                logging.info(f"Cleaned up {affected_rows} old records (older than {days_to_keep} days)")
                return affected_rows
                
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return 0
    
    def close_connection(self):
        """Close the database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()
            logging.info("Database connection closed")
    
    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close_connection()

    def check_ticker_exists_today(self, ticker):
        """Check if a record already exists for this ticker today"""
        return self._check_ticker_exists_in_window(ticker, hours=24)
    
    def check_ticker_exists_last_24h(self, ticker):
        """Check if a record already exists for this ticker in the last 24 hours"""
        return self._check_ticker_exists_in_window(ticker, hours=24)
    
    def check_ticker_exists_in_window(self, ticker, hours=24):
        """Check if a record already exists for this ticker within the specified hours window"""
        if self.fallback_mode:
            logging.info(f"FALLBACK MODE: Would check if {ticker} exists in last {hours} hours")
            return False
        
        try:
            from datetime import datetime, timedelta
            
            # Calculate the time window
            now = datetime.now()
            window_start = now - timedelta(hours=hours)
            
            check_sql = """
            SELECT id, scraped_at FROM scraped_data 
            WHERE ticker = %s 
            AND scraped_at >= %s
            LIMIT 1;
            """
            
            with self.connection.cursor() as cursor:
                cursor.execute(check_sql, (ticker, window_start))
                result = cursor.fetchone()
                
                if result:
                    record_id, scraped_at = result
                    time_diff = now - scraped_at
                    hours_diff = time_diff.total_seconds() / 3600
                    logging.debug(f"Found existing record for {ticker} from {hours_diff:.1f} hours ago")
                    return True
                else:
                    logging.debug(f"No recent record found for {ticker} in last {hours} hours")
                    return False
                    
        except Exception as e:
            logging.error(f"Error checking if {ticker} exists in last {hours} hours: {e}")
            # If we can't check, assume it doesn't exist to be safe
            return False
    
    def get_tickers_without_recent_data(self, ticker_list, hours=24):
        """Get list of tickers that don't have data within the specified hours window"""
        if self.fallback_mode:
            logging.info(f"FALLBACK MODE: Would check {len(ticker_list)} tickers for data in last {hours} hours")
            return ticker_list
        
        if not ticker_list:
            return []
        
        try:
            from datetime import datetime, timedelta
            
            # Calculate the time window
            now = datetime.now()
            window_start = now - timedelta(hours=hours)
            
            # Get all tickers with recent data
            check_sql = """
            SELECT DISTINCT ticker FROM scraped_data 
            WHERE scraped_at >= %s;
            """
            
            recent_tickers = set()
            with self.connection.cursor() as cursor:
                cursor.execute(check_sql, (window_start,))
                results = cursor.fetchall()
                recent_tickers = {row[0] for row in results}
            
            # Filter out tickers with recent data
            tickers_without_data = [ticker for ticker in ticker_list if ticker not in recent_tickers]
            
            logging.info(f"Found {len(recent_tickers)} tickers with data in last {hours} hours")
            logging.info(f"Filtered to {len(tickers_without_data)} tickers without recent data")
            
            return tickers_without_data
                    
        except Exception as e:
            logging.error(f"Error filtering tickers by recent data: {e}")
            # If we can't check, return all tickers to be safe
            return ticker_list
