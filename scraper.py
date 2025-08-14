import os
import requests
from bs4 import BeautifulSoup
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from dotenv import load_dotenv
import schedule
import time
from datetime import datetime
import logging
import json
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Remove file handler for debugging
    ]
)

class YahooFinanceScraper:
    def __init__(self):
        # Initialize ScrapingBee API
        self.scrapingbee_api_key = os.getenv('SCRAPINGBEE_API_KEY')
        if not self.scrapingbee_api_key:
            raise ValueError("SCRAPINGBEE_API_KEY not found in environment variables")
        
        # Initialize Nhost GraphQL client (optional for now)
        nhost_url = os.getenv('NHOST_URL')
        nhost_admin_secret = os.getenv('NHOST_ADMIN_SECRET')
        
        if nhost_url and nhost_admin_secret:
            # Create GraphQL client with admin secret for full access
            transport = RequestsHTTPTransport(
                url=f"{nhost_url}/v1/graphql",
                headers={
                    'x-hasura-admin-secret': nhost_admin_secret,
                    'Content-Type': 'application/json',
                }
            )
            self.graphql_client = Client(transport=transport, fetch_schema_from_transport=True)
            self.use_nhost = True
        else:
            self.use_nhost = False
            logging.info("Nhost credentials not found, running in local mode only")
        
        # Base URL for Yahoo Finance analysis
        self.base_url = "https://finance.yahoo.com/quote/{}/analysis/"
        
        # Base URL for Yahoo Finance summary
        self.summary_url = "https://finance.yahoo.com/quote/{}/"
        
        # For debugging: Always use PTON
        self.stocks = ['PTON']
        logging.info("DEBUG MODE: Using PTON ticker only")
        
    def load_stocks(self):
        """Load stock tickers from stocks.txt file - DISABLED FOR DEBUGGING"""
        # Always return PTON for debugging
        return ['PTON']
    
    def scrape_website(self, ticker):
        """Scrape Yahoo Finance analysis page using ScrapingBee"""
        try:
            url = self.base_url.format(ticker)
            logging.info(f"Starting to scrape with ScrapingBee: {url}")
            
            # ScrapingBee API endpoint
            api_url = "https://app.scrapingbee.com/api/v1/"
            
            # Parameters for ScrapingBee
            params = {
                'api_key': self.scrapingbee_api_key,
                'url': url,
                'render_js': 'true',  # Yahoo Finance needs JavaScript rendering
                'premium_proxy': 'true',  # Use premium proxies for better success rate
                'country_code': 'us',  # Specify country for proxy
                'wait': '1000'  # Wait 5 seconds for JavaScript to load
            }
            
            # Make the request to ScrapingBee
            response = requests.get(api_url, params=params)
            
            if response.status_code == 200:
                logging.info(f"Successfully retrieved page content for {ticker}")
                return response.text
            else:
                logging.error(f"ScrapingBee API error for {ticker}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error during ScrapingBee scraping {ticker}: {str(e)}")
            return None
    
    def scrape_summary_page(self, ticker):
        """Scrape Yahoo Finance summary page using ScrapingBee"""
        try:
            url = self.summary_url.format(ticker)
            logging.info(f"Starting to scrape summary page with ScrapingBee: {url}")
            
            # ScrapingBee API endpoint
            api_url = "https://app.scrapingbee.com/api/v1/"
            
            # Parameters for ScrapingBee
            params = {
                'api_key': self.scrapingbee_api_key,
                'url': url,
                'render_js': 'true',  # Yahoo Finance needs JavaScript rendering
                'premium_proxy': 'true',  # Use premium proxies for better success rate
                'country_code': 'us',  # Specify country for proxy
                'wait': '1000'  # Wait 1 second for JavaScript to load
            }
            
            # Make the request to ScrapingBee
            response = requests.get(api_url, params=params)
            
            if response.status_code == 200:
                logging.info(f"Successfully retrieved summary page content for {ticker}")
                return response.text
            else:
                logging.error(f"ScrapingBee API error for summary page {ticker}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error during ScrapingBee summary scraping {ticker}: {str(e)}")
            return None
    
    def extract_quote_statistics(self, html_content):
        """Extract quote statistics from the summary page"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the quote statistics section
            quote_stats_div = soup.find('div', {'data-testid': 'quote-statistics'})
            if not quote_stats_div:
                logging.warning("Quote statistics section not found")
                return {}
            
            quote_stats = {}
            
            # Find all list items in the quote statistics
            list_items = quote_stats_div.find_all('li')
            
            for item in list_items:
                label_span = item.find('span', class_='label')
                value_span = item.find('span', class_='value')
                
                if label_span and value_span:
                    label = label_span.get('title', label_span.get_text(strip=True))
                    value = value_span.get_text(strip=True)
                    
                    # Clean and parse the value based on the label
                    parsed_value = self._parse_quote_value(label, value)
                    if parsed_value is not None:
                        quote_stats[label.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('&', 'and')] = parsed_value
            
            logging.info(f"Extracted {len(quote_stats)} quote statistics")
            return quote_stats
            
        except Exception as e:
            logging.warning(f"Error extracting quote statistics: {str(e)}")
            return {}
    
    def _parse_quote_value(self, label, value):
        """Parse quote value based on the label type"""
        try:
            if value == '--' or value == '':
                return None
            
            # Handle different types of values
            if 'price' in label.lower() or 'close' in label.lower() or 'open' in label.lower() or 'bid' in label.lower() or 'ask' in label.lower():
                # Extract numeric price from text
                import re
                price_match = re.search(r'[\d.]+', value)
                if price_match:
                    return float(price_match.group())
                return None
            
            elif 'range' in label.lower():
                # Handle ranges like "8.02 - 8.41" or "2.83 - 10.90"
                import re
                range_match = re.search(r'([\d.]+)\s*-\s*([\d.]+)', value)
                if range_match:
                    low, high = float(range_match.group(1)), float(range_match.group(2))
                    if 'day' in label.lower():
                        return {'day_low': low, 'day_high': high}
                    elif '52' in label.lower() or 'week' in label.lower():
                        return {'week_52_low': low, 'week_52_high': high}
                return None
            
            elif 'volume' in label.lower():
                # Handle volume numbers like "11,834,966"
                import re
                volume_match = re.search(r'[\d,]+', value)
                if volume_match:
                    volume_str = volume_match.group().replace(',', '')
                    return int(volume_str)
                return None
            
            elif 'market cap' in label.lower():
                # Handle market cap like "3.319B"
                return value
            
            elif 'beta' in label.lower():
                # Handle beta value
                try:
                    return float(value)
                except:
                    return None
            
            elif 'pe ratio' in label.lower() or 'eps' in label.lower():
                # Handle PE ratio and EPS
                if value == '--':
                    return None
                try:
                    return float(value)
                except:
                    return None
            
            elif 'target' in label.lower():
                # Handle target price
                try:
                    return float(value)
                except:
                    return None
            
            else:
                # For other fields, return as string
                return value
                
        except Exception as e:
            logging.debug(f"Error parsing value '{value}' for label '{label}': {str(e)}")
            return value
    
    def parse_yahoo_finance_content(self, html_content, ticker, summary_html_content=None):
        """Parse Yahoo Finance analysis page HTML and extract relevant data"""
        if not html_content:
            return None
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            ticker_data = {
                'ticker': ticker,
                'scraped_at': datetime.now().isoformat(),
                'url': self.base_url.format(ticker),
                'data': {}
            }
            
            # Extract all prices using the unified approach
            all_prices = self._extract_all_prices(soup)
            if all_prices:
                ticker_data['data'].update(all_prices)
                logging.info(f"Extracted {len(all_prices)} price types: {list(all_prices.keys())}")
            
            # Extract quote statistics from summary page if provided
            if summary_html_content:
                quote_stats = self.extract_quote_statistics(summary_html_content)
                if quote_stats:
                    # Process the quote statistics to extract individual values
                    self._process_quote_statistics(ticker_data['data'], quote_stats)
                    logging.info(f"Extracted {len(quote_stats)} quote statistics")
            
            logging.info(f"Parsed content for {ticker}")
            return ticker_data
            
        except Exception as e:
            logging.error(f"Error parsing content for {ticker}: {str(e)}")
            return None
    
    def _process_quote_statistics(self, data, quote_stats):
        """Process quote statistics and add them to the data dictionary"""
        try:
            for key, value in quote_stats.items():
                if isinstance(value, dict):
                    # Handle range values (day range, 52 week range)
                    data.update(value)
                else:
                    # Handle single values
                    data[key] = value
            
            # Handle special cases for bid/ask sizes
            if 'bid' in quote_stats:
                bid_text = quote_stats.get('bid', '')
                if 'x' in bid_text:
                    parts = bid_text.split('x')
                    if len(parts) == 2:
                        try:
                            data['bid_price'] = float(parts[0].strip())
                            data['bid_size'] = int(parts[1].strip().replace(',', ''))
                        except:
                            pass
            
            if 'ask' in quote_stats:
                ask_text = quote_stats.get('ask', '')
                if 'x' in ask_text:
                    parts = ask_text.split('x')
                    if len(parts) == 2:
                        try:
                            data['ask_price'] = float(parts[0].strip())
                            data['ask_size'] = int(parts[1].strip().replace(',', ''))
                        except:
                            pass
            
            # Also handle the mapped bid/ask fields
            if 'bid' in data:
                bid_text = data.get('bid', '')
                if 'x' in bid_text:
                    parts = bid_text.split('x')
                    if len(parts) == 2:
                        try:
                            data['bid_price'] = float(parts[0].strip())
                            data['bid_size'] = int(parts[1].strip().replace(',', ''))
                        except:
                            pass
                # Remove the original bid field
                data.pop('bid', None)
            
            if 'ask' in data:
                ask_text = data.get('ask', '')
                if 'x' in ask_text:
                    parts = ask_text.split('x')
                    if len(parts) == 2:
                        try:
                            data['ask_price'] = float(parts[0].strip())
                            data['ask_size'] = int(parts[1].strip().replace(',', ''))
                        except:
                            pass
                # Remove the original ask field
                data.pop('ask', None)
            
            # Map the extracted values to the database column names
            mapping = {
                'previous_close': 'previous_close',
                'open': 'open_price',
                'bid': 'bid',  # Will be processed separately for bid_price and bid_size
                'ask': 'ask',  # Will be processed separately for ask_price and ask_size
                'day\'s_range': 'day_range',  # This will be split into day_low and day_high
                '52_week_range': 'week_52_range',  # This will be split into week_52_low and week_52_high
                'volume': 'volume',
                'avg._volume': 'avg_volume',
                'market_cap_intraday': 'market_cap',
                'beta_5y_monthly': 'beta',
                'pe_ratio_ttm': 'pe_ratio_ttm',
                'eps_ttm': 'eps_ttm',
                'earnings_date': 'earnings_date',
                'forward_dividend_and_yield': 'forward_dividend',
                'ex-dividend_date': 'ex_dividend_date',
                '1y_target_est': 'target_1y'
            }
            
            # Apply the mapping
            for old_key, new_key in mapping.items():
                if old_key in data:
                    data[new_key] = data.pop(old_key)
                    
        except Exception as e:
            logging.warning(f"Error processing quote statistics: {str(e)}")
    
    def _extract_all_prices(self, soup):
        """Extract all prices and styles from priceContainer divs"""
        try:
            prices = {}
            price_styles = {}
            
            # Find all divs with class 'priceContainer'
            price_containers = soup.find_all('div', class_=lambda x: x and 'priceContainer' in x)
            
            logging.info(f"Found {len(price_containers)} priceContainer divs")
            
            for container in price_containers:
                container_classes = container.get('class', [])
                logging.info(f"Price container classes: {container_classes}")
                
                # Determine the type based on classes
                price_type = None
                if 'low' in container_classes:
                    price_type = 'price_low'
                elif 'average' in container_classes:
                    price_type = 'price_average'
                elif 'current' in container_classes:
                    price_type = 'price_current'
                elif 'high' in container_classes:
                    price_type = 'price_high'
                
                if price_type:
                    # Extract price value
                    price_span = container.find('span', class_='price')
                    if price_span:
                        price_text = price_span.get_text(strip=True)
                        price_text = price_text.replace('$', '').replace(',', '').replace('USD', '').strip()
                        
                        try:
                            price_value = float(price_text)
                            prices[price_type] = price_value
                            logging.info(f"Successfully extracted {price_type}: {price_value}")
                        except ValueError as e:
                            logging.warning(f"Could not convert price text '{price_text}' to float: {str(e)}")
                    else:
                        logging.debug(f"No price div found in {price_type} container")
                    
                    # For average price type, extract left/right percentage value
                    if price_type == 'price_average':
                        import re
                        style_text = container.get('style', '')
                        
                        # Extract left percentage
                        left_match = re.search(r'left:\s*([\d.]+)%', style_text)
                        if left_match:
                            price_percent = float(left_match.group(1))
                            price_styles['price_percent'] = price_percent
                            logging.info(f"Extracted price percentage: {price_percent}%")
                        
                        # Extract right percentage (if left not found)
                        else:
                            right_match = re.search(r'right:\s*([\d.]+)%', style_text)
                            if right_match:
                                price_percent = float(right_match.group(1))
                                price_styles['price_percent'] = price_percent
                                logging.info(f"Extracted price percentage: {price_percent}%")
                    
                else:
                    logging.debug(f"Could not determine price type for container with classes: {container_classes}")
            
            # Combine prices and styles into a single result
            result = prices.copy()
            result.update(price_styles)
            
            return result if result else None
            
        except Exception as e:
            logging.warning(f"Error extracting all prices: {str(e)}")
            return None
    
    def save_to_nhost(self, data_items):
        """Save extracted data to Nhost database using GraphQL - DISABLED FOR DEBUGGING"""
        logging.info("DEBUG MODE: Skipping Nhost save")
        return None
    
    def save_to_json_file(self, data_items, filename=None):
        """Save extracted data to a JSON file - DISABLED FOR DEBUGGING"""
        logging.info("DEBUG MODE: Skipping file save")
        return None
    
    def run_scraping_job(self):
        """Main method to run the complete scraping job for all stocks"""
        try:
            logging.info("Starting Yahoo Finance scraping job in DEBUG MODE")
            
            all_data = []
            
            for ticker in self.stocks:
                logging.info(f"Processing ticker: {ticker}")
                
                # Step 1: Scrape the analysis page
                html_content = self.scrape_website(ticker)
                
                # Step 2: Scrape the summary page
                summary_html_content = self.scrape_summary_page(ticker)
                
                # Step 3: Parse the content (both analysis and summary)
                if html_content:
                    ticker_data = self.parse_yahoo_finance_content(html_content, ticker, summary_html_content)
                    
                    if ticker_data:
                        all_data.append(ticker_data)
                        logging.info(f"Successfully processed {ticker}")
                        
                        # DEBUG: Show extracted data
                        print("\n" + "="*50)
                        print(f"EXTRACTED DATA FOR {ticker}:")
                        print("="*50)
                        print(json.dumps(ticker_data, indent=2))
                        print("="*50 + "\n")
                    else:
                        logging.warning(f"No data extracted for {ticker}")
                else:
                    logging.error(f"Failed to retrieve page content for {ticker}")
                
                # Add delay between requests to be respectful
                #time.sleep(2)
            
            # Step 3: Save data - DISABLED FOR DEBUGGING
            if all_data:
                logging.info(f"DEBUG MODE: Scraping job completed. Processed {len(all_data)} tickers")
                logging.info("DEBUG MODE: Data extraction completed - no files saved")
            else:
                logging.warning("No data extracted from any ticker")
                
        except Exception as e:
            logging.error(f"Error in scraping job: {str(e)}")

def main():
    """Main function to run the scraper in DEBUG MODE"""
    scraper = None
    try:
        scraper = YahooFinanceScraper()
        
        if not scraper.stocks:
            logging.error("No stocks loaded. Please check stocks.txt file.")
            return
        
        # Run the scraping job immediately in DEBUG MODE
        scraper.run_scraping_job()
        
        logging.info("DEBUG MODE: Scraper completed. No scheduling or file saving.")
        
    except KeyboardInterrupt:
        logging.info("Scraper stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
    finally:
        # Always close the browser
        # The browser is no longer used, so this block is removed.
        pass

if __name__ == "__main__":
    main() 