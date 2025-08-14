#!/usr/bin/env python3
"""
Script to scrape all stock tickers from stockanalysis.com using their API endpoint
"""
import os
import requests
import time
import logging
import json
from typing import List, Dict, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class StockAnalysisTickerScraper:
    def __init__(self):
        """Initialize the ticker scraper"""
        self.scrapingbee_api_key = os.getenv('SCRAPINGBEE_API_KEY')
        if not self.scrapingbee_api_key:
            raise ValueError("SCRAPINGBEE_API_KEY not found in environment variables")
        
        self.base_url = "https://stockanalysis.com/api/screener/s/f"
        self.logger = logging.getLogger(__name__)
    
    def scrape_page(self, page_number: int) -> Dict[str, Any]:
        """
        Scrape a specific page using the API endpoint
        
        Args:
            page_number: Page number to scrape
            
        Returns:
            Dictionary containing page data and tickers
        """
        # Construct the API URL with parameters
        api_params = {
            'm': 's',           # market
            's': 'asc',         # sort order
            'c': 's,n,industry,marketCap',  # columns: symbol, name, industry, market cap
            'cn': '500',        # count per page
            'p': str(page_number),  # page number
            'i': 'stocks'       # instrument type
        }
        
        url = f"{self.base_url}?{'&'.join([f'{k}={v}' for k, v in api_params.items()])}"
        self.logger.info(f"Scraping page {page_number} using API: {url}")
        
        try:
            # ScrapingBee parameters
            params = {
                'api_key': self.scrapingbee_api_key,
                'url': url,
                'render_js': 'false',  # No need for JavaScript rendering for API calls
                'premium_proxy': 'true',
                'country_code': 'us',
                'block_ads': 'false',  # No ads in API responses
                'block_resources': 'false',
                'wait': '1000',  # Shorter wait for API calls
            }
            
            response = requests.get('https://app.scrapingbee.com/api/v1/', params=params)
            response.raise_for_status()
            
            # Parse the JSON response
            try:
                data = response.json()
                self.logger.info(f"API response received for page {page_number}")
                # Log the structure to help debug
                if isinstance(data, dict):
                    self.logger.info(f"Response keys: {list(data.keys())}")
                    if 'data' in data and isinstance(data['data'], dict):
                        self.logger.info(f"data['data'] keys: {list(data['data'].keys())}")
            except json.JSONDecodeError:
                self.logger.warning(f"Response is not JSON for page {page_number}: {response.text[:200]}...")
                return {'page': page_number, 'tickers': [], 'has_next': False, 'error': 'Invalid JSON response'}
            
            # Extract tickers from the API response
            tickers = self._extract_tickers_from_api_response(data, page_number)
            
            # Check if there's a next page (if we got 500 tickers, there might be more)
            has_next = len(tickers) == 500
            
            self.logger.info(f"Page {page_number}: Found {len(tickers)} tickers, has_next: {has_next}")
            
            return {
                'page': page_number,
                'tickers': tickers,
                'has_next': has_next,
                'url': url,
                'page_info': f"Page {page_number} (API)"
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error scraping page {page_number}: {e}")
            return {'page': page_number, 'tickers': [], 'has_next': False, 'error': str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error scraping page {page_number}: {e}")
            return {'page': page_number, 'tickers': [], 'has_next': False, 'error': str(e)}
    
    def _extract_tickers_from_api_response(self, data: Dict[str, Any], page_number: int) -> List[Dict[str, Any]]:
        """
        Extract ticker data from the API response
        
        Args:
            data: API response data
            page_number: Page number for logging
            
        Returns:
            List of ticker dictionaries
        """
        tickers = []
        
        try:
            # The API response structure is data['data']['data']
            if isinstance(data, dict):
                # Check for the nested structure: data['data']['data']
                if 'data' in data and isinstance(data['data'], dict):
                    if 'data' in data['data'] and isinstance(data['data']['data'], list):
                        raw_tickers = data['data']['data']
                        self.logger.info(f"Found ticker data in data['data']['data'] structure")
                    else:
                        # Fallback: try to find any list in the response
                        raw_tickers = None
                        for key, value in data.items():
                            if isinstance(value, list) and len(value) > 0:
                                raw_tickers = value
                                break
                        
                        if raw_tickers is None:
                            self.logger.warning(f"No ticker data found in API response for page {page_number}")
                            return tickers
                else:
                    # Try to find any list in the response as fallback
                    raw_tickers = None
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) > 0:
                            raw_tickers = value
                            break
                    
                    if raw_tickers is None:
                        self.logger.warning(f"No ticker data found in API response for page {page_number}")
                        return tickers
                
                # Process each ticker
                for ticker_item in raw_tickers:
                    if isinstance(ticker_item, dict):
                        ticker_data = {}
                        
                        # Extract symbol (usually 's' or 'symbol')
                        ticker_data['symbol'] = ticker_item.get('s') or ticker_item.get('symbol') or ticker_item.get('ticker', '')
                        
                        # Extract company name (usually 'n' or 'name')
                        ticker_data['company_name'] = ticker_item.get('n') or ticker_item.get('name') or ''
                        
                        # Extract industry
                        ticker_data['industry'] = ticker_item.get('industry') or ''
                        
                        # Extract market cap
                        ticker_data['market_cap'] = ticker_item.get('marketCap') or ticker_item.get('market_cap') or ''
                        
                        # Only add if we have at least a symbol
                        if ticker_data['symbol']:
                            tickers.append(ticker_data)
                
                self.logger.info(f"Successfully extracted {len(tickers)} tickers from API response")
                
            else:
                self.logger.warning(f"Unexpected API response format for page {page_number}: {type(data)}")
                
        except Exception as e:
            self.logger.error(f"Error extracting tickers from API response: {e}")
        
        return tickers
    
    def scrape_all_tickers(self, max_pages: int = None, delay: float = 2.0) -> List[Dict[str, Any]]:
        """
        Scrape all available ticker pages
        
        Args:
            max_pages: Maximum number of pages to scrape (None for unlimited)
            delay: Delay between page requests in seconds
            
        Returns:
            List of all tickers found
        """
        all_tickers = []
        total_pages_scraped = 0
        
        self.logger.info(f"Starting to scrape all tickers (max_pages: {max_pages})")
        
        page_number = 1
        while True:
            # Check if we've reached the maximum pages
            if max_pages and total_pages_scraped >= max_pages:
                self.logger.info(f"Reached maximum pages limit: {max_pages}")
                break
            
            # Scrape the current page
            page_data = self.scrape_page(page_number)
            
            if page_data.get('error'):
                self.logger.error(f"Failed to scrape page {page_number}: {page_data['error']}")
                break
            
            # Add tickers from this page
            page_tickers = page_data.get('tickers', [])
            all_tickers.extend(page_tickers)
            
            total_pages_scraped += 1
            self.logger.info(f"Page {page_number}: Added {len(page_tickers)} tickers. Total so far: {len(all_tickers)}")
            
            # Check if there's a next page
            if not page_data.get('has_next', False):
                self.logger.info("No more pages available")
                break
            
            # Move to next page
            page_number += 1
            
            # Delay before next request to be respectful
            if delay > 0:
                time.sleep(delay)
        
        self.logger.info(f"Scraping completed. Total pages: {total_pages_scraped}, Total tickers: {len(all_tickers)}")
        return all_tickers
    
    def save_tickers_to_file(self, tickers: List[Dict[str, Any]], filename: str = 'all_tickers.json'):
        """
        Save tickers to a JSON file
        
        Args:
            tickers: List of ticker dictionaries
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'total_tickers': len(tickers),
                    'tickers': tickers
                }, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(tickers)} tickers to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving tickers to file: {e}")
    
    def save_tickers_to_txt(self, tickers: List[Dict[str, Any]], filename: str = 'all_tickers.txt'):
        """
        Save ticker symbols to a simple text file (one per line)
        
        Args:
            tickers: List of ticker dictionaries
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for ticker in tickers:
                    symbol = ticker.get('symbol', '')
                    if symbol:
                        f.write(f"{symbol}\n")
            
            self.logger.info(f"Saved {len(tickers)} ticker symbols to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving ticker symbols to file: {e}")


def main():
    """Main function to run the ticker scraper"""
    try:
        scraper = StockAnalysisTickerScraper()
        
        # Scrape all tickers (limit to 10 pages for testing)
        print("Starting ticker scraping...")
        tickers = scraper.scrape_all_tickers(max_pages=10, delay=3.0)
        
        if tickers:
            print(f"\nSuccessfully scraped {len(tickers)} tickers!")
            
            # Save to JSON file
            scraper.save_tickers_to_file(tickers, 'all_tickers_api.json')
            
            # Save to simple text file
            scraper.save_tickers_to_txt(tickers, 'all_tickers_api.txt')
            
            # Display first few tickers as preview
            print("\nFirst 10 tickers:")
            for i, ticker in enumerate(tickers[:10]):
                print(f"{i+1}. {ticker.get('symbol', 'N/A')} - {ticker.get('company_name', 'N/A')}")
            
            if len(tickers) > 10:
                print(f"... and {len(tickers) - 10} more")
        else:
            print("No tickers were scraped. Check the logs for errors.")
            
    except Exception as e:
        print(f"Error running ticker scraper: {e}")
        logging.error(f"Error running ticker scraper: {e}")


if __name__ == "__main__":
    main()
