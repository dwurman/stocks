#!/usr/bin/env python3
"""
Investigate pagination structure on stockanalysis.com
"""
import os
import requests
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PaginationInvestigator:
    def __init__(self):
        """Initialize the pagination investigator"""
        self.scrapingbee_api_key = os.getenv('SCRAPINGBEE_API_KEY')
        if not self.scrapingbee_api_key:
            raise ValueError("SCRAPINGBEE_API_KEY not found in environment variables")
        
        self.base_url = "https://stockanalysis.com/stocks/"
        self.logger = logging.getLogger(__name__)
    
    def investigate_page_structure(self, page=1):
        """Investigate the structure of a specific page"""
        url = f"{self.base_url}?page={page}" if page > 1 else self.base_url
        
        self.logger.info(f"Investigating page {page}: {url}")
        
        # ScrapingBee parameters
        params = {
            'api_key': self.scrapingbee_api_key,
            'url': url,
            'render_js': 'true',
            'premium_proxy': 'true',
            'country_code': 'us',
            'block_ads': 'true',
            'wait': '5000',  # Wait 5 seconds for page to load
        }
        
        try:
            response = requests.get('https://app.scrapingbee.com/api/v1/', params=params)
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for pagination elements
            self._find_pagination_elements(soup, page)
            
            # Look for the main table
            self._find_main_table(soup, page)
            
            # Look for any page indicators
            self._find_page_indicators(soup, page)
            
        except Exception as e:
            self.logger.error(f"Error investigating page {page}: {e}")
    
    def _find_pagination_elements(self, soup, page):
        """Find pagination elements"""
        print(f"\n=== PAGINATION ELEMENTS FOR PAGE {page} ===")
        
        # Look for common pagination patterns
        pagination_selectors = [
            'nav[aria-label="Pagination"]',
            '.pagination',
            '.pager',
            '.page-numbers',
            '[class*="pagination"]',
            '[class*="pager"]',
            '[class*="page"]'
        ]
        
        for selector in pagination_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Found pagination with selector: {selector}")
                for elem in elements:
                    print(f"  Content: {elem.get_text(strip=True)[:200]}...")
                    print(f"  HTML: {str(elem)[:300]}...")
        
        # Look for next/previous buttons
        next_buttons = soup.find_all('a', string=lambda text: text and any(word in text.lower() for word in ['next', '>', '»']))
        prev_buttons = soup.find_all('a', string=lambda text: text and any(word in text.lower() for word in ['previous', '<', '«']))
        
        if next_buttons:
            print(f"Found {len(next_buttons)} next buttons:")
            for btn in next_buttons:
                print(f"  Next: {btn.get_text(strip=True)} - href: {btn.get('href', 'N/A')}")
        
        if prev_buttons:
            print(f"Found {len(prev_buttons)} previous buttons:")
            for btn in prev_buttons:
                print(f"  Previous: {btn.get_text(strip=True)} - href: {btn.get('href', 'N/A')}")
        
        # Look for page numbers
        page_links = soup.find_all('a', href=lambda href: href and 'page=' in href)
        if page_links:
            print(f"Found {len(page_links)} page links:")
            for link in page_links:
                print(f"  Page link: {link.get_text(strip=True)} - href: {link.get('href', 'N/A')}")
    
    def _find_main_table(self, soup, page):
        """Find the main table structure"""
        print(f"\n=== MAIN TABLE STRUCTURE FOR PAGE {page} ===")
        
        # Look for the main table wrapper
        main_table_wrap = soup.find('div', id='main-table-wrap')
        if main_table_wrap:
            print("Found main-table-wrap div")
            
            # Look for table
            table = main_table_wrap.find('table')
            if table:
                rows = table.find_all('tr')
                print(f"  Table found with {len(rows)} rows")
                
                # Check if there are more rows than expected
                if len(rows) > 500:
                    print(f"  Large number of rows: {len(rows)} - might be all tickers on one page")
                else:
                    print(f"  Standard number of rows: {len(rows)}")
            else:
                print("  No table found within main-table-wrap")
        else:
            print("main-table-wrap div not found")
    
    def _find_page_indicators(self, soup, page):
        """Find page indicators and total counts"""
        print(f"\n=== PAGE INDICATORS FOR PAGE {page} ===")
        
        # Look for text that might indicate total count
        page_text = soup.get_text()
        
        # Look for patterns like "showing X of Y" or "page X of Y"
        import re
        
        # Look for "showing X of Y" patterns
        showing_pattern = r'showing\s+(\d+)\s+of\s+(\d+)'
        showing_matches = re.findall(showing_pattern, page_text, re.IGNORECASE)
        if showing_matches:
            print(f"Found 'showing X of Y' patterns: {showing_matches}")
        
        # Look for "page X of Y" patterns
        page_pattern = r'page\s+(\d+)\s+of\s+(\d+)'
        page_matches = re.findall(page_pattern, page_text, re.IGNORECASE)
        if page_matches:
            print(f"Found 'page X of Y' patterns: {page_matches}")
        
        # Look for total count patterns
        total_pattern = r'total.*?(\d+)'
        total_matches = re.findall(total_pattern, page_text, re.IGNORECASE)
        if total_matches:
            print(f"Found total count patterns: {total_matches}")
    
    def test_multiple_pages(self):
        """Test multiple pages to see the structure"""
        print("=== TESTING MULTIPLE PAGES ===")
        
        for page in [1, 2, 3]:
            print(f"\n{'='*50}")
            self.investigate_page_structure(page)
            print(f"{'='*50}")

def main():
    """Main function"""
    try:
        investigator = PaginationInvestigator()
        investigator.test_multiple_pages()
        
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
