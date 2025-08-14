#!/usr/bin/env python3
"""
Debug script to examine the exact HTML structure of pagination elements
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

class PaginationDebugger:
    def __init__(self):
        """Initialize the pagination debugger"""
        self.scrapingbee_api_key = os.getenv('SCRAPINGBEE_API_KEY')
        if not self.scrapingbee_api_key:
            raise ValueError("SCRAPINGBEE_API_KEY not found in environment variables")
        
        self.base_url = "https://stockanalysis.com/stocks/"
        self.logger = logging.getLogger(__name__)
    
    def debug_pagination(self):
        """Debug the pagination structure"""
        url = self.base_url
        
        self.logger.info(f"Debugging pagination for: {url}")
        
        # ScrapingBee parameters
        params = {
            'api_key': self.scrapingbee_api_key,
            'url': url,
            'render_js': 'true',
            'premium_proxy': 'true',
            'country_code': 'us',
            'block_ads': 'true',
            'wait': '5000',
        }
        
        try:
            response = requests.get('https://app.scrapingbee.com/api/v1/', params=params)
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print("=== FULL PAGE TEXT ===")
            page_text = soup.get_text()
            print(page_text[:2000])  # First 2000 characters
            
            print("\n=== LOOKING FOR PAGINATION ELEMENTS ===")
            
            # Look for any element containing "Next"
            next_elements = soup.find_all(string=lambda text: text and 'Next' in text)
            print(f"Found {len(next_elements)} elements containing 'Next' text:")
            for i, elem in enumerate(next_elements):
                print(f"  {i+1}. Text: '{elem}'")
                print(f"     Parent: {elem.parent}")
                print(f"     Parent tag: {elem.parent.name if elem.parent else 'None'}")
                if elem.parent:
                    print(f"     Parent attrs: {elem.parent.attrs}")
                    print(f"     Parent HTML: {str(elem.parent)[:300]}...")
                print()
            
            # Look for any element containing "next" (lowercase)
            next_lower_elements = soup.find_all(string=lambda text: text and 'next' in text.lower())
            print(f"Found {len(next_lower_elements)} elements containing 'next' text (case-insensitive):")
            for i, elem in enumerate(next_lower_elements):
                print(f"  {i+1}. Text: '{elem}'")
                print(f"     Parent: {elem.parent}")
                if elem.parent:
                    print(f"     Parent HTML: {str(elem.parent)[:300]}...")
                print()
            
            # Look for any button elements
            buttons = soup.find_all('button')
            print(f"Found {len(buttons)} button elements:")
            for i, btn in enumerate(buttons):
                print(f"  {i+1}. Button: {btn.get_text(strip=True)}")
                print(f"     Attrs: {btn.attrs}")
                print(f"     HTML: {str(btn)[:300]}...")
                print()
            
            # Look for any link elements
            links = soup.find_all('a')
            print(f"Found {len(links)} link elements:")
            for i, link in enumerate(links):
                text = link.get_text(strip=True)
                href = link.get('href', '')
                if 'next' in text.lower() or 'next' in href.lower():
                    print(f"  {i+1}. Link: '{text}' -> {href}")
                    print(f"     Attrs: {link.attrs}")
                    print(f"     HTML: {str(link)[:300]}...")
                    print()
            
            # Look for any span elements
            spans = soup.find_all('span')
            print(f"Found {len(spans)} span elements:")
            for i, span in enumerate(spans):
                text = span.get_text(strip=True)
                if 'next' in text.lower():
                    print(f"  {i+1}. Span: '{text}'")
                    print(f"     Parent: {span.parent}")
                    if span.parent:
                        print(f"     Parent HTML: {str(span.parent)[:300]}...")
                    print()
            
            # Look for any div elements with pagination-related classes
            pagination_divs = soup.find_all('div', class_=lambda x: x and any(word in x.lower() for word in ['pagination', 'pager', 'page', 'nav']))
            print(f"Found {len(pagination_divs)} divs with pagination-related classes:")
            for i, div in enumerate(pagination_divs):
                print(f"  {i+1}. Div class: {div.get('class', [])}")
                print(f"     Text: {div.get_text(strip=True)[:200]}...")
                print(f"     HTML: {str(div)[:500]}...")
                print()
            
        except Exception as e:
            self.logger.error(f"Error debugging pagination: {e}")
            print(f"Error: {e}")

def main():
    """Main function"""
    try:
        debugger = PaginationDebugger()
        debugger.debug_pagination()
        
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
