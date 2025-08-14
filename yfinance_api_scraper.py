#!/usr/bin/env python3
"""
Yahoo Finance API Scraper using yfinance library
Simplified to only use Ticker.info data for maximum reliability
Now supports batch processing using yf.Tickers()
"""

import yfinance as yf
import logging
from datetime import datetime
import json
import time
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class YahooFinanceAPIScraper:
    def __init__(self):
        """Initialize the API scraper"""
        self.logger = logging.getLogger(__name__)
        
    def get_ticker_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive ticker information using yfinance API - only Ticker.info"""
        try:
            self.logger.info(f"Fetching data for {ticker} via yfinance API...")
            
            # Create ticker object
            ticker_obj = yf.Ticker(ticker)
            
            # Get basic info - this contains all the data we need
            info = ticker_obj.info
            
            # Compile all data from info object
            ticker_data = {
                'ticker': ticker,
                'scraped_at': datetime.now().isoformat(),
                'data': {
                    # Basic company information
                    'company_name': info.get('longName', 'N/A'),
                    'long_name': info.get('longName', 'N/A'),
                    'short_name': info.get('shortName', 'N/A'),
                    'sector': info.get('sector', 'N/A'),
                    'industry': info.get('industry', 'N/A'),
                    'website': info.get('website', 'N/A'),
                    'business_summary': info.get('longBusinessSummary', 'N/A'),
                    'country': info.get('country', 'N/A'),
                    'currency': info.get('currency', 'N/A'),
                    'exchange': info.get('exchange', 'N/A'),
                    'quote_type': info.get('quoteType', 'N/A'),
                    
                    # Market data
                    'market_cap': info.get('marketCap', 'N/A'),
                    'enterprise_value': info.get('enterpriseValue', 'N/A'),
                    'float_shares': info.get('floatShares', 'N/A'),
                    'shares_outstanding': info.get('sharesOutstanding', 'N/A'),
                    'shares_short': info.get('sharesShort', 'N/A'),
                    'shares_short_prev_month': info.get('sharesShortPriorMonth', 'N/A'),
                    'shares_short_prior_month': info.get('sharesShortPriorMonth', 'N/A'),
                    
                    # Price data
                    'current_price': info.get('currentPrice', 'N/A'),
                    'previous_close': info.get('previousClose', 'N/A'),
                    'open': info.get('open', 'N/A'),
                    'day_low': info.get('dayLow', 'N/A'),
                    'day_high': info.get('dayHigh', 'N/A'),
                    'fifty_two_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
                    'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                    'fifty_day_average': info.get('fiftyDayAverage', 'N/A'),
                    'two_hundred_day_average': info.get('twoHundredDayAverage', 'N/A'),
                    
                    # Volume and trading
                    'volume': info.get('volume', 'N/A'),
                    'average_volume': info.get('averageVolume', 'N/A'),
                    'average_volume_10days': info.get('averageVolume10days', 'N/A'),
                    'bid': info.get('bid', 'N/A'),
                    'ask': info.get('ask', 'N/A'),
                    'bid_size': info.get('bidSize', 'N/A'),
                    'ask_size': info.get('askSize', 'N/A'),
                    
                    # Financial ratios
                    'trailing_pe': info.get('trailingPE', 'N/A'),
                    'forward_pe': info.get('forwardPE', 'N/A'),
                    'peg_ratio': info.get('pegRatio', 'N/A'),
                    'price_to_book': info.get('priceToBook', 'N/A'),
                    'price_to_sales_trailing_12_months': info.get('priceToSalesTrailing12Months', 'N/A'),
                    'debt_to_equity': info.get('debtToEquity', 'N/A'),
                    'return_on_equity': info.get('returnOnEquity', 'N/A'),
                    'return_on_assets': info.get('returnOnAssets', 'N/A'),
                    
                    # Earnings and dividends
                    'trailing_eps': info.get('trailingEps', 'N/A'),
                    'forward_eps': info.get('forwardEps', 'N/A'),
                    'dividend_yield': info.get('dividendYield', 'N/A'),
                    'dividend_rate': info.get('dividendRate', 'N/A'),
                    'payout_ratio': info.get('payoutRatio', 'N/A'),
                    'five_year_avg_dividend_yield': info.get('fiveYearAvgDividendYield', 'N/A'),
                    
                    # Growth metrics
                    'revenue_growth': info.get('revenueGrowth', 'N/A'),
                    'earnings_growth': info.get('earningsGrowth', 'N/A'),
                    'profit_margins': info.get('profitMargins', 'N/A'),
                    'operating_margins': info.get('operatingMargins', 'N/A'),
                    'ebitda_margins': info.get('ebitdaMargins', 'N/A'),
                    
                    # Additional metrics
                    'beta': info.get('beta', 'N/A'),
                    'book_value': info.get('bookValue', 'N/A'),
                    'short_ratio': info.get('shortRatio', 'N/A'),
                    'price_target_low': info.get('targetLowPrice', 'N/A'),
                    'price_target_mean': info.get('targetMeanPrice', 'N/A'),
                    'price_target_high': info.get('targetHighPrice', 'N/A'),
                    'price_target_median': info.get('targetMedianPrice', 'N/A'),
                    
                    # Market status
                    'regular_market_time': info.get('regularMarketTime', 'N/A'),
                    'regular_market_open': info.get('regularMarketOpen', 'N/A'),
                    'regular_market_close': info.get('regularMarketClose', 'N/A'),
                    'regular_market_previous_close': info.get('regularMarketPreviousClose', 'N/A'),
                }
            }
            
            self.logger.info(f"Successfully fetched data for {ticker}")
            return ticker_data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {ticker}: {str(e)}")
            return None
    
    def get_batch_tickers_info(self, tickers: List[str], batch_size: int = 10) -> List[Dict[str, Any]]:
        """Get data for multiple tickers using yfinance batch functionality"""
        try:
            self.logger.info(f"Fetching batch data for {len(tickers)} tickers in batches of {batch_size}")
            
            all_results = []
            
            # Process tickers in batches
            for i in range(0, len(tickers), batch_size):
                batch_tickers = tickers[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (len(tickers) + batch_size - 1) // batch_size
                
                self.logger.info(f"Processing batch {batch_num}/{total_batches}: {len(batch_tickers)} tickers")
                
                try:
                    # Create batch ticker object using yf.Tickers()
                    ticker_symbols = ' '.join(batch_tickers)
                    batch_tickers_obj = yf.Tickers(ticker_symbols)
                    
                    batch_results = []
                    for ticker in batch_tickers:
                        try:
                            # Access individual ticker data from the batch
                            ticker_obj = batch_tickers_obj.tickers[ticker]
                            info = ticker_obj.info
                            
                            # Compile all data from info object
                            ticker_data = {
                                'ticker': ticker,
                                'scraped_at': datetime.now().isoformat(),
                                'data': {
                                    # Basic company information
                                    'company_name': info.get('longName', 'N/A'),
                                    'long_name': info.get('longName', 'N/A'),
                                    'short_name': info.get('shortName', 'N/A'),
                                    'sector': info.get('sector', 'N/A'),
                                    'industry': info.get('industry', 'N/A'),
                                    'website': info.get('website', 'N/A'),
                                    'business_summary': info.get('longBusinessSummary', 'N/A'),
                                    'country': info.get('country', 'N/A'),
                                    'currency': info.get('currency', 'N/A'),
                                    'exchange': info.get('exchange', 'N/A'),
                                    'quote_type': info.get('quoteType', 'N/A'),
                                    
                                    # Market data
                                    'market_cap': info.get('marketCap', 'N/A'),
                                    'enterprise_value': info.get('enterpriseValue', 'N/A'),
                                    'float_shares': info.get('floatShares', 'N/A'),
                                    'shares_outstanding': info.get('sharesOutstanding', 'N/A'),
                                    'shares_short': info.get('sharesShort', 'N/A'),
                                    'shares_short_prev_month': info.get('sharesShortPriorMonth', 'N/A'),
                                    'shares_short_prior_month': info.get('sharesShortPriorMonth', 'N/A'),
                                    
                                    # Price data
                                    'current_price': info.get('currentPrice', 'N/A'),
                                    'previous_close': info.get('previousClose', 'N/A'),
                                    'open': info.get('open', 'N/A'),
                                    'day_low': info.get('dayLow', 'N/A'),
                                    'day_high': info.get('dayHigh', 'N/A'),
                                    'fifty_two_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
                                    'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                                    'fifty_day_average': info.get('fiftyDayAverage', 'N/A'),
                                    'two_hundred_day_average': info.get('twoHundredDayAverage', 'N/A'),
                                    
                                    # Volume and trading
                                    'volume': info.get('volume', 'N/A'),
                                    'average_volume': info.get('averageVolume', 'N/A'),
                                    'average_volume_10days': info.get('averageVolume10days', 'N/A'),
                                    'bid': info.get('bid', 'N/A'),
                                    'ask': info.get('ask', 'N/A'),
                                    'bid_size': info.get('bidSize', 'N/A'),
                                    'ask_size': info.get('askSize', 'N/A'),
                                    
                                    # Financial ratios
                                    'trailing_pe': info.get('trailingPE', 'N/A'),
                                    'forward_pe': info.get('forwardPE', 'N/A'),
                                    'peg_ratio': info.get('pegRatio', 'N/A'),
                                    'price_to_book': info.get('priceToBook', 'N/A'),
                                    'price_to_sales_trailing_12_months': info.get('priceToSalesTrailing12Months', 'N/A'),
                                    'debt_to_equity': info.get('debtToEquity', 'N/A'),
                                    'return_on_equity': info.get('returnOnEquity', 'N/A'),
                                    'return_on_assets': info.get('returnOnAssets', 'N/A'),
                                    
                                    # Earnings and dividends
                                    'trailing_eps': info.get('trailingEps', 'N/A'),
                                    'forward_eps': info.get('forwardEps', 'N/A'),
                                    'dividend_yield': info.get('dividendYield', 'N/A'),
                                    'dividend_rate': info.get('dividendRate', 'N/A'),
                                    'payout_ratio': info.get('payoutRatio', 'N/A'),
                                    'five_year_avg_dividend_yield': info.get('fiveYearAvgDividendYield', 'N/A'),
                                    
                                    # Growth metrics
                                    'revenue_growth': info.get('revenueGrowth', 'N/A'),
                                    'earnings_growth': info.get('earningsGrowth', 'N/A'),
                                    'profit_margins': info.get('profitMargins', 'N/A'),
                                    'operating_margins': info.get('operatingMargins', 'N/A'),
                                    'ebitda_margins': info.get('ebitdaMargins', 'N/A'),
                                    
                                    # Additional metrics
                                    'beta': info.get('beta', 'N/A'),
                                    'book_value': info.get('bookValue', 'N/A'),
                                    'short_ratio': info.get('shortRatio', 'N/A'),
                                    'price_target_low': info.get('targetLowPrice', 'N/A'),
                                    'price_target_mean': info.get('targetMeanPrice', 'N/A'),
                                    'price_target_high': info.get('targetHighPrice', 'N/A'),
                                    'price_target_median': info.get('targetMedianPrice', 'N/A'),
                                    
                                    # Market status
                                    'regular_market_time': info.get('regularMarketTime', 'N/A'),
                                    'regular_market_open': info.get('regularMarketOpen', 'N/A'),
                                    'regular_market_close': info.get('regularMarketClose', 'N/A'),
                                    'regular_market_previous_close': info.get('regularMarketPreviousClose', 'N/A'),
                                }
                            }
                            
                            batch_results.append(ticker_data)
                            self.logger.info(f"Successfully fetched data for {ticker}")
                            
                        except Exception as e:
                            self.logger.error(f"Error fetching data for {ticker}: {str(e)}")
                            continue
                    
                    all_results.extend(batch_results)
                    self.logger.info(f"✅ Batch {batch_num} completed successfully with {len(batch_results)} tickers")
                    
                except Exception as e:
                    self.logger.error(f"Error processing batch {batch_num}: {str(e)}")
                    # Fallback to individual ticker fetching for this batch
                    self.logger.info(f"Falling back to individual ticker fetching for batch {batch_num}")
                    for ticker in batch_tickers:
                        try:
                            ticker_data = self.get_ticker_info(ticker)
                            if ticker_data:
                                all_results.append(ticker_data)
                        except Exception as fallback_error:
                            self.logger.error(f"Fallback failed for {ticker}: {str(fallback_error)}")
                            continue
            
            self.logger.info(f"Batch processing completed. Successfully fetched {len(all_results)} out of {len(tickers)} tickers")
            return all_results
            
        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            return []
    
    def get_multiple_tickers(self, tickers: List[str], delay: float = 0.1) -> List[Dict[str, Any]]:
        """Get data for multiple tickers with rate limiting (legacy method)"""
        results = []
        
        for i, ticker in enumerate(tickers):
            try:
                self.logger.info(f"Processing {i+1}/{len(tickers)}: {ticker}")
                
                ticker_data = self.get_ticker_info(ticker)
                if ticker_data:
                    results.append(ticker_data)
                
                # Rate limiting to be respectful to the API
                if i < len(tickers) - 1:  # Don't sleep after the last ticker
                    time.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"Error processing {ticker}: {e}")
                continue
        
        self.logger.info(f"Successfully processed {len(results)} out of {len(tickers)} tickers")
        return results
    
    def save_to_json(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """Save data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"yfinance_data_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"Data saved to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {e}")
            return None
    
    def display_summary(self, data: List[Dict[str, Any]]) -> None:
        """Display a summary of the fetched data"""
        if not data:
            print("No data to display")
            return
        
        print(f"\n{'='*80}")
        print(f"YAHOO FINANCE API DATA SUMMARY")
        print(f"{'='*80}")
        print(f"Total tickers processed: {len(data)}")
        print(f"Data fetched at: {data[0]['scraped_at']}")
        
        for ticker_data in data[:5]:  # Show first 5 tickers
            ticker = ticker_data['ticker']
            info = ticker_data['data']
            
            print(f"\n{ticker}: {info.get('company_name', 'N/A')}")
            print(f"  Sector: {info.get('sector', 'N/A')}")
            print(f"  Current Price: ${info.get('current_price', 'N/A')}")
            print(f"  Market Cap: {info.get('market_cap', 'N/A')}")
            print(f"  PE Ratio: {info.get('trailing_pe', 'N/A')}")
            print(f"  Volume: {info.get('volume', 'N/A'):,}" if info.get('volume') else "  Volume: N/A")
        
        if len(data) > 5:
            print(f"\n... and {len(data) - 5} more tickers")

def main():
    """Main function to demonstrate the API scraper"""
    try:
        # Initialize the scraper
        scraper = YahooFinanceAPIScraper()
        
        # Test with a few tickers
        test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
        
        print("🚀 Starting Yahoo Finance API scraper...")
        print(f"📊 Fetching data for {len(test_tickers)} tickers...")
        
        # Test batch functionality
        print("\n🔄 Testing batch functionality...")
        batch_data = scraper.get_batch_tickers_info(test_tickers, batch_size=3)
        
        if batch_data:
            # Display summary
            scraper.display_summary(batch_data)
            
            # Save to file
            filename = scraper.save_to_json(batch_data)
            if filename:
                print(f"\n✅ Data saved to: {filename}")
            
            print(f"\n🎉 Successfully processed {len(batch_data)} tickers using batch mode!")
        else:
            print("❌ No data was fetched")
            
    except Exception as e:
        logging.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
