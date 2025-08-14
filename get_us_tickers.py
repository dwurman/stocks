#!/usr/bin/env python3
"""
Script to fetch US stock tickers from major indices using yfinance
"""

import yfinance as yf
import pandas as pd
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class USStockTickerFetcher:
    def __init__(self):
        """Initialize the ticker fetcher"""
        self.tickers = {}
        self.logger = logging.getLogger(__name__)
        
    def get_sp500_tickers(self):
        """Get S&P 500 tickers"""
        try:
            self.logger.info("Fetching S&P 500 tickers...")
            
            # Method 1: Try to get from Wikipedia via yfinance
            try:
                sp500 = yf.Tickers('^GSPC')
                # Get the components from S&P 500
                sp500_info = sp500.tickers['^GSPC'].info
                if 'components' in sp500_info:
                    components = sp500_info['components']
                    self.tickers['S&P 500'] = components
                    self.logger.info(f"Found {len(components)} S&P 500 tickers")
                    return components
            except Exception as e:
                self.logger.warning(f"Could not get S&P 500 components: {e}")
            
            # Method 2: Use a known list of major S&P 500 companies
            sp500_major = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'BRK-B', 'LLY', 'V', 'TSM',
                'UNH', 'XOM', 'JNJ', 'JPM', 'PG', 'AVGO', 'HD', 'CVX', 'ABBV', 'PEP',
                'KO', 'BAC', 'PFE', 'TMO', 'COST', 'DHR', 'MRK', 'ACN', 'WMT', 'ABT',
                'VZ', 'TXN', 'CMCSA', 'ADBE', 'NFLX', 'PM', 'INTC', 'QCOM', 'IBM', 'T',
                'ORCL', 'HON', 'LOW', 'UPS', 'AMD', 'INTU', 'SPGI', 'GILD', 'ISRG', 'RTX'
            ]
            
            self.tickers['S&P 500'] = sp500_major
            self.logger.info(f"Using fallback list of {len(sp500_major)} major S&P 500 tickers")
            return sp500_major
            
        except Exception as e:
            self.logger.error(f"Error fetching S&P 500 tickers: {e}")
            return []
    
    def get_nasdaq_tickers(self):
        """Get NASDAQ tickers (top companies)"""
        try:
            self.logger.info("Fetching NASDAQ tickers...")
            
            # Get top NASDAQ companies
            nasdaq_major = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'NFLX', 'ADBE',
                'INTC', 'AMD', 'QCOM', 'ORCL', 'INTU', 'PYPL', 'CSCO', 'CMCSA', 'PEP',
                'COST', 'HON', 'GILD', 'ISRG', 'REGN', 'VRTX', 'BIIB', 'ALGN', 'IDXX',
                'KLAC', 'LRCX', 'AMAT', 'MU', 'ADI', 'AVGO', 'TXN', 'QCOM', 'SWKS'
            ]
            
            self.tickers['NASDAQ'] = nasdaq_major
            self.logger.info(f"Found {len(nasdaq_major)} major NASDAQ tickers")
            return nasdaq_major
            
        except Exception as e:
            self.logger.error(f"Error fetching NASDAQ tickers: {e}")
            return []
    
    def get_dow_jones_tickers(self):
        """Get Dow Jones Industrial Average tickers"""
        try:
            self.logger.info("Fetching Dow Jones tickers...")
            
            # Dow Jones 30 components
            dow_tickers = [
                'AAPL', 'MSFT', 'UNH', 'HD', 'GS', 'AMGN', 'CAT', 'JPM', 'JNJ', 'V',
                'PG', 'TRV', 'CVX', 'MRK', 'KO', 'PFE', 'IBM', 'T', 'AXP', 'WMT',
                'DIS', 'BA', 'MMM', 'DOW', 'CSCO', 'INTC', 'VZ', 'NKE', 'HON', 'CRM'
            ]
            
            self.tickers['Dow Jones'] = dow_tickers
            self.logger.info(f"Found {len(dow_tickers)} Dow Jones tickers")
            return dow_tickers
            
        except Exception as e:
            self.logger.error(f"Error fetching Dow Jones tickers: {e}")
            return []
    
    def get_etf_tickers(self):
        """Get major ETF tickers"""
        try:
            self.logger.info("Fetching major ETF tickers...")
            
            etf_tickers = [
                'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO', 'BND', 'TLT',
                'GLD', 'SLV', 'USO', 'XLE', 'XLF', 'XLK', 'XLV', 'XLI', 'XLP', 'XLY'
            ]
            
            self.tickers['ETFs'] = etf_tickers
            self.logger.info(f"Found {len(etf_tickers)} major ETF tickers")
            return etf_tickers
            
        except Exception as e:
            self.logger.error(f"Error fetching ETF tickers: {e}")
            return []
    
    def get_all_tickers(self):
        """Get all tickers from all sources"""
        try:
            self.logger.info("Fetching all US stock tickers...")
            
            # Get tickers from all sources
            self.get_sp500_tickers()
            self.get_nasdaq_tickers()
            self.get_dow_jones_tickers()
            self.get_etf_tickers()
            
            # Combine all tickers and remove duplicates
            all_tickers = []
            for source, tickers in self.tickers.items():
                all_tickers.extend(tickers)
            
            # Remove duplicates while preserving order
            unique_tickers = list(dict.fromkeys(all_tickers))
            
            self.logger.info(f"Total unique tickers found: {len(unique_tickers)}")
            return unique_tickers
            
        except Exception as e:
            self.logger.error(f"Error fetching all tickers: {e}")
            return []
    
    def save_tickers_to_file(self, filename=None):
        """Save tickers to a file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"us_tickers_{timestamp}.txt"
        
        try:
            all_tickers = self.get_all_tickers()
            
            with open(filename, 'w') as f:
                for ticker in all_tickers:
                    f.write(f"{ticker}\n")
            
            self.logger.info(f"Saved {len(all_tickers)} tickers to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error saving tickers to file: {e}")
            return None
    
    def save_detailed_info_to_json(self, filename=None):
        """Save detailed ticker information to JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"us_tickers_detailed_{timestamp}.json"
        
        try:
            # Get all tickers first
            all_tickers = self.get_all_tickers()
            
            # Create detailed info structure
            detailed_info = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_tickers': len(all_tickers),
                    'sources': list(self.tickers.keys())
                },
                'tickers_by_source': self.tickers,
                'all_tickers': all_tickers
            }
            
            with open(filename, 'w') as f:
                json.dump(detailed_info, f, indent=2)
            
            self.logger.info(f"Saved detailed ticker info to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error saving detailed info to JSON: {e}")
            return None
    
    def display_summary(self):
        """Display a summary of all tickers"""
        try:
            all_tickers = self.get_all_tickers()
            
            print("\n" + "="*60)
            print("US STOCK TICKERS SUMMARY")
            print("="*60)
            
            for source, tickers in self.tickers.items():
                print(f"\n{source}: {len(tickers)} tickers")
                print("-" * 40)
                # Display first 10 tickers from each source
                display_tickers = tickers[:10]
                print(", ".join(display_tickers))
                if len(tickers) > 10:
                    print(f"... and {len(tickers) - 10} more")
            
            print(f"\n{'='*60}")
            print(f"TOTAL UNIQUE TICKERS: {len(all_tickers)}")
            print(f"{'='*60}")
            
            # Show first 20 unique tickers
            print("\nFirst 20 unique tickers:")
            print(", ".join(all_tickers[:20]))
            if len(all_tickers) > 20:
                print(f"... and {len(all_tickers) - 20} more")
                
        except Exception as e:
            self.logger.error(f"Error displaying summary: {e}")

def main():
    """Main function"""
    try:
        fetcher = USStockTickerFetcher()
        
        # Display summary
        fetcher.display_summary()
        
        # Save to files
        txt_file = fetcher.save_tickers_to_file()
        json_file = fetcher.save_detailed_info_to_json()
        
        if txt_file and json_file:
            print(f"\n✅ Tickers saved to:")
            print(f"   📄 Simple list: {txt_file}")
            print(f"   📊 Detailed info: {json_file}")
        
    except Exception as e:
        logging.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
