#!/usr/bin/env python3
"""
Yahoo Finance API Scraper
Provides comprehensive data extraction from yfinance API
"""

import yfinance as yf
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YahooFinanceAPIScraper:
    """Scraper for Yahoo Finance API using yfinance library"""
    
    def __init__(self, use_scrapingbee: bool = False):
        """
        Initialize the scraper
        
        Args:
            use_scrapingbee: Whether to use ScrapingBee proxy (placeholder for future use)
        """
        self.use_scrapingbee = use_scrapingbee
        if self.use_scrapingbee:
            logger.info("ScrapingBee configured but bypassed for yfinance calls")
        
        # Rate limiting
        self.request_delay = 0.1  # 100ms between requests
        
    def _get_single_ticker_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive information for a single ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with ticker data or None if failed
        """
        try:
            logger.info(f"Fetching data for {ticker}")
            
            # Create ticker object
            stock = yf.Ticker(ticker)
            
            # Get basic info
            info = stock.info
            
            if not info or len(info) < 10:
                logger.warning(f"Insufficient data for {ticker}")
                return None
            
            # Extract and format data
            ticker_data = {
                'ticker': ticker,
                'scraped_at': datetime.now(),
                'data': {
                    # Company info
                    'long_name': info.get('longName', ''),
                    'short_name': info.get('shortName', ''),
                    'sector': info.get('sector', ''),
                    'industry': info.get('industry', ''),
                    'country': info.get('country', ''),
                    'website': info.get('website', ''),
                    'business_summary': info.get('longBusinessSummary', ''),
                    
                    # Market data
                    'market_cap': info.get('marketCap'),
                    'current_price': info.get('currentPrice'),
                    'previous_close': info.get('previousClose'),
                    'open': info.get('open'),
                    'day_low': info.get('dayLow'),
                    'day_high': info.get('dayHigh'),
                    'volume': info.get('volume'),
                    'avg_volume': info.get('averageVolume'),
                    'exchange': info.get('exchange', ''),
                    
                    # Financial metrics
                    'trailing_pe': info.get('trailingPE'),
                    'forward_pe': info.get('forwardPE'),
                    'price_to_book': info.get('priceToBook'),
                    'price_to_sales': info.get('priceToSalesTrailing12Months'),
                    'beta': info.get('beta'),
                    'dividend_yield': info.get('dividendYield'),
                    'dividend_rate': info.get('dividendRate'),
                    'payout_ratio': info.get('payoutRatio'),
                    
                    # Analyst data
                    'target_mean_price': info.get('targetMeanPrice'),
                    'target_median_price': info.get('targetMedianPrice'),
                    'target_high_price': info.get('targetHighPrice'),
                    'target_low_price': info.get('targetLowPrice'),
                    'recommendation_key': info.get('recommendationKey', ''),
                    'number_of_analyst_opinions': info.get('numberOfAnalystOpinions'),
                    
                    # Performance
                    'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                    'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                    'fifty_day_average': info.get('fiftyDayAverage'),
                    'two_hundred_day_average': info.get('twoHundredDayAverage'),
                    
                    # Additional metrics
                    'enterprise_value': info.get('enterpriseValue'),
                    'debt_to_equity': info.get('debtToEquity'),
                    'return_on_equity': info.get('returnOnEquity'),
                    'return_on_assets': info.get('returnOnAssets'),
                    'profit_margins': info.get('profitMargins'),
                    'operating_margins': info.get('operatingMargins'),
                    'ebitda_margins': info.get('ebitdaMargins'),
                    'revenue_growth': info.get('revenueGrowth'),
                    'earnings_growth': info.get('earningsGrowth'),
                    'revenue_per_share': info.get('revenuePerShare'),
                    'return_on_capital': info.get('returnOnCapital'),
                    'quick_ratio': info.get('quickRatio'),
                    'current_ratio': info.get('currentRatio'),
                    'total_cash': info.get('totalCash'),
                    'total_debt': info.get('totalDebt'),
                    'total_revenue': info.get('totalRevenue'),
                    'gross_profits': info.get('grossProfits'),
                    'free_cashflow': info.get('freeCashflow'),
                    'operating_cashflow': info.get('operatingCashflow'),
                    'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth'),
                    'revenue_quarterly_growth': info.get('revenueQuarterlyGrowth'),
                    'earnings_annual_growth': info.get('earningsAnnualGrowth'),
                    'revenue_annual_growth': info.get('revenueAnnualGrowth'),
                    'earnings_annual_rate': info.get('earningsAnnualRate'),
                    'revenue_annual_rate': info.get('revenueAnnualRate'),
                    'price_to_cash_per_share': info.get('priceToCashPerShare'),
                    'price_to_free_cashflow': info.get('priceToFreeCashflow'),
                    'book_value': info.get('bookValue'),
                    'cash_per_share': info.get('cashPerShare'),
                    'free_cashflow_per_share': info.get('freeCashflowPerShare'),
                    'enterprise_to_revenue': info.get('enterpriseToRevenue'),
                    'enterprise_to_ebitda': info.get('enterpriseToEbitda'),
                    'earnings_yield': info.get('earningsYield'),
                    'forward_earnings_yield': info.get('forwardEarningsYield'),
                    'debt_to_equity': info.get('debtToEquity'),
                    'net_income_to_common': info.get('netIncomeToCommon'),
                    'trailing_eps': info.get('trailingEps'),
                    'forward_eps': info.get('forwardEps'),
                    'peg_ratio': info.get('pegRatio'),
                    'price_to_sales_trailing_12_months': info.get('priceToSalesTrailing12Months'),
                    'enterprise_value_multiple': info.get('enterpriseValueMultiple'),
                    'price_to_book': info.get('priceToBook'),
                    'ev_to_revenue': info.get('evToRevenue'),
                    'ev_to_ebitda': info.get('evToEbitda'),
                    'market_cap_change_24h': info.get('marketCapChange24h'),
                    'market_cap_change': info.get('marketCapChange'),
                    'price_change_24h': info.get('priceChange24h'),
                    'price_change': info.get('priceChange'),
                    'volume_change_24h': info.get('volumeChange24h'),
                    'volume_change': info.get('volumeChange'),
                    'average_volume_10days': info.get('averageVolume10days'),
                    'average_volume_3months': info.get('averageVolume3months'),
                    'shares_outstanding': info.get('sharesOutstanding'),
                    'float_shares': info.get('floatShares'),
                    'shares_short': info.get('sharesShort'),
                    'shares_short_prior_month': info.get('sharesShortPriorMonth'),
                    'shares_short_previous_month_date': info.get('sharesShortPreviousMonthDate'),
                    'date_short_interest': info.get('dateShortInterest'),
                    'shares_percent_shares_out': info.get('sharesPercentSharesOut'),
                    'held_percent_insiders': info.get('heldPercentInsiders'),
                    'held_percent_institutions': info.get('heldPercentInstitutions'),
                    'short_ratio': info.get('shortRatio'),
                    'short_percent_of_float': info.get('shortPercentOfFloat'),
                    'shares_short_prior_month': info.get('sharesShortPriorMonth'),
                    'forward_annual_dividend_rate': info.get('forwardAnnualDividendRate'),
                    'forward_annual_dividend_yield': info.get('forwardAnnualDividendYield'),
                    'trailing_annual_dividend_rate': info.get('trailingAnnualDividendRate'),
                    'trailing_annual_dividend_yield': info.get('trailingAnnualDividendYield'),
                    'five_year_avg_dividend_yield': info.get('fiveYearAvgDividendYield'),
                    'payout_ratio': info.get('payoutRatio'),
                    'dividend_date': info.get('dividendDate'),
                    'ex_dividend_date': info.get('exDividendDate'),
                    'last_split_factor': info.get('lastSplitFactor'),
                    'last_split_date': info.get('lastSplitDate'),
                    'enterprise_to_revenue': info.get('enterpriseToRevenue'),
                    'enterprise_to_ebitda': info.get('enterpriseToEbitda'),
                    'earnings_yield': info.get('earningsYield'),
                    'forward_earnings_yield': info.get('forwardEarningsYield'),
                    'debt_to_equity': info.get('debtToEquity'),
                    'net_income_to_common': info.get('netIncomeToCommon'),
                    'trailing_eps': info.get('trailingEps'),
                    'forward_eps': info.get('forwardEps'),
                    'peg_ratio': info.get('pegRatio'),
                    'price_to_sales_trailing_12_months': info.get('priceToSalesTrailing12Months'),
                    'enterprise_value_multiple': info.get('enterpriseValueMultiple'),
                    'price_to_book': info.get('priceToBook'),
                    'ev_to_revenue': info.get('evToRevenue'),
                    'ev_to_ebitda': info.get('evToEbitda'),
                    'market_cap_change_24h': info.get('marketCapChange24h'),
                    'market_cap_change': info.get('marketCapChange'),
                    'price_change_24h': info.get('priceChange24h'),
                    'price_change': info.get('priceChange'),
                    'volume_change_24h': info.get('volumeChange24h'),
                    'volume_change': info.get('volumeChange'),
                    'average_volume_10days': info.get('averageVolume10days'),
                    'average_volume_3months': info.get('averageVolume3months'),
                    'shares_outstanding': info.get('sharesOutstanding'),
                    'float_shares': info.get('floatShares'),
                    'shares_short': info.get('sharesShort'),
                    'shares_short_prior_month': info.get('sharesShortPriorMonth'),
                    'shares_short_previous_month_date': info.get('sharesShortPreviousMonthDate'),
                    'date_short_interest': info.get('dateShortInterest'),
                    'shares_percent_shares_out': info.get('sharesPercentSharesOut'),
                    'held_percent_insiders': info.get('heldPercentInsiders'),
                    'held_percent_institutions': info.get('heldPercentInstitutions'),
                    'short_ratio': info.get('shortRatio'),
                    'short_percent_of_float': info.get('shortPercentOfFloat'),
                    'shares_short_prior_month': info.get('sharesShortPriorMonth'),
                    'forward_annual_dividend_rate': info.get('forwardAnnualDividendRate'),
                    'forward_annual_dividend_yield': info.get('forwardAnnualDividendYield'),
                    'trailing_annual_dividend_rate': info.get('trailingAnnualDividendRate'),
                    'trailing_annual_dividend_yield': info.get('trailingAnnualDividendYield'),
                    'five_year_avg_dividend_yield': info.get('fiveYearAvgDividendYield'),
                    'payout_ratio': info.get('payoutRatio'),
                    'dividend_date': info.get('dividendDate'),
                    'ex_dividend_date': info.get('exDividendDate'),
                    'last_split_factor': info.get('lastSplitFactor'),
                    'last_split_date': info.get('lastSplitDate')
                }
            }
            
            # Clean up None values and convert to appropriate types
            for key, value in ticker_data['data'].items():
                if value is None:
                    ticker_data['data'][key] = ''
                elif isinstance(value, float) and value != value:  # Check for NaN
                    ticker_data['data'][key] = ''
            
            logger.info(f"Successfully fetched data for {ticker}")
            return ticker_data
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None
    
    def get_ticker_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get ticker info (alias for _get_single_ticker_info)
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with ticker data or None if failed
        """
        return self._get_single_ticker_info(ticker)
    
    def get_batch_tickers_info(self, tickers: List[str], batch_size: int = 10) -> List[Dict[str, Any]]:
        """
        Get information for multiple tickers in batches
        
        Args:
            tickers: List of stock ticker symbols
            batch_size: Number of tickers to process in each batch
            
        Returns:
            List of dictionaries with ticker data
        """
        results = []
        
        # Process tickers in batches
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}: {batch}")
            
            for ticker in batch:
                try:
                    ticker_data = self._get_single_ticker_info(ticker)
                    if ticker_data:
                        results.append(ticker_data)
                    
                    # Rate limiting
                    if self.request_delay > 0:
                        time.sleep(self.request_delay)
                        
                except Exception as e:
                    logger.error(f"Error processing {ticker}: {e}")
                    continue
        
        logger.info(f"Successfully processed {len(results)} out of {len(tickers)} tickers")
        return results
    
    def get_tickers_info(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """
        Get information for multiple tickers (alias for get_batch_tickers_info)
        
        Args:
            tickers: List of stock ticker symbols
            
        Returns:
            List of dictionaries with ticker data
        """
        return self.get_batch_tickers_info(tickers)
