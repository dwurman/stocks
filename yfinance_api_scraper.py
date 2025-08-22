#!/usr/bin/env python3
"""
Yahoo Finance API Scraper using yfinance library
Simplified to only use Ticker.info data for maximum reliability
Now supports batch processing using yf.Tickers()
"""

import os
from dotenv import load_dotenv
import yfinance as yf
from curl_cffi import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class YahooFinanceAPIScraper:
    def __init__(self, use_scrapingbee: bool = False, scrapingbee_api_key: Optional[str] = None):
        """Initialize the API scraper.

        If use_scrapingbee is True, yfinance will use a curl_cffi session routed via ScrapingBee proxy.
        """
        self.logger = logging.getLogger(__name__)
        self.session: Optional[requests.Session] = None

        if use_scrapingbee:
            api_key = scrapingbee_api_key or os.getenv('SCRAPINGBEE_API_KEY')
            if not api_key:
                self.logger.warning("use_scrapingbee=True but SCRAPINGBEE_API_KEY not set; continuing without proxy")
            else:
                self.session = self._create_scrapingbee_session(api_key)

    def _create_scrapingbee_session(self, api_key: str) -> requests.Session:
        """Create a curl_cffi session configured to use ScrapingBee proxy for all HTTP/HTTPS."""
        session = requests.Session()
        # ScrapingBee standard proxy endpoint
        proxy_host = os.getenv('SCRAPINGBEE_PROXY_HOST', 'proxy.scrapingbee.com')
        proxy_port = os.getenv('SCRAPINGBEE_PROXY_PORT', '8886')
        proxy_auth_user = os.getenv('SCRAPINGBEE_PROXY_USER', 'scrapingbee')
        proxy_url = f"http://{proxy_auth_user}:{api_key}@{proxy_host}:{proxy_port}"
        session.proxies.update({
            'http': proxy_url,
            'https': proxy_url,
        })
        # Reasonable timeouts and headers on the session
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; yahoof-scraper/1.0)'
        })
        return session
        
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
                    # Create batch ticker object using yf.Tickers(), optionally with proxy session
                    ticker_symbols = ' '.join(batch_tickers)
                    if self.session:
                        batch_tickers_obj = yf.Tickers(ticker_symbols, session=self.session)
                    else:
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
                                    # Company Information
                                    'long_name': info.get('longName'),
                                    'short_name': info.get('shortName'),
                                    'long_business_summary': info.get('longBusinessSummary'),
                                    'website': info.get('website'),
                                    'phone': info.get('phone'),
                                    'address1': info.get('address1'),
                                    'city': info.get('city'),
                                    'state': info.get('state'),
                                    'zip': info.get('zip'),
                                    'country': info.get('country'),
                                    'full_time_employees': info.get('fullTimeEmployees'),
                                    'industry': info.get('industry'),
                                    'industry_key': info.get('industryKey'),
                                    'industry_disp': info.get('industryDisp'),
                                    'sector': info.get('sector'),
                                    'sector_key': info.get('sectorKey'),
                                    'sector_disp': info.get('sectorDisp'),
                                    'ir_website': info.get('irWebsite'),
                                    'language': info.get('language'),
                                    'region': info.get('region'),
                                    'type_disp': info.get('typeDisp'),
                                    'display_name': info.get('displayName'),
                                    'symbol': info.get('symbol'),
                                    
                                    # Market Data
                                    'market_cap': info.get('marketCap'),
                                    'enterprise_value': info.get('enterpriseValue'),
                                    'current_price': info.get('currentPrice'),
                                    'regular_market_price': info.get('regularMarketPrice'),
                                    'previous_close': info.get('previousClose'),
                                    'open': info.get('open'),
                                    'day_low': info.get('dayLow'),
                                    'day_high': info.get('dayHigh'),
                                    'regular_market_open': info.get('regularMarketOpen'),
                                    'regular_market_day_low': info.get('regularMarketDayLow'),
                                    'regular_market_day_high': info.get('regularMarketDayHigh'),
                                    'regular_market_previous_close': info.get('regularMarketPreviousClose'),
                                    'regular_market_change': info.get('regularMarketChange'),
                                    'regular_market_change_percent': info.get('regularMarketChangePercent'),
                                    'regular_market_day_range': info.get('regularMarketDayRange'),
                                    'regular_market_time': info.get('regularMarketTime'),
                                    'regular_market_volume': info.get('regularMarketVolume'),
                                    'volume': info.get('volume'),
                                    'average_volume': info.get('averageVolume'),
                                    'average_volume_10days': info.get('averageVolume10days'),
                                    'average_daily_volume_10_day': info.get('averageDailyVolume10Day'),
                                    'average_daily_volume_3_month': info.get('averageDailyVolume3Month'),
                                    
                                    # Price Data
                                    'price_hint': info.get('priceHint'),
                                    'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                                    'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                                    'fifty_two_week_low_change': info.get('fiftyTwoWeekLowChange'),
                                    'fifty_two_week_low_change_percent': info.get('fiftyTwoWeekLowChangePercent'),
                                    'fifty_two_week_high_change': info.get('fiftyTwoWeekHighChange'),
                                    'fifty_two_week_high_change_percent': info.get('fiftyTwoWeekHighChangePercent'),
                                    'fifty_two_week_range': info.get('fiftyTwoWeekRange'),
                                    'fifty_two_week_change_percent': info.get('fiftyTwoWeekChangePercent'),
                                    'fifty_day_average': info.get('fiftyDayAverage'),
                                    'fifty_day_average_change': info.get('fiftyDayAverageChange'),
                                    'fifty_day_average_change_percent': info.get('fiftyDayAverageChangePercent'),
                                    'two_hundred_day_average': info.get('twoHundredDayAverage'),
                                    'two_hundred_day_average_change': info.get('twoHundredDayAverageChange'),
                                    'two_hundred_day_average_change_percent': info.get('twoHundredDayAverageChangePercent'),
                                    'sandp_52_week_change': info.get('SandP52WeekChange'),
                                    
                                    # Trading Information
                                    'bid': info.get('bid'),
                                    'ask': info.get('ask'),
                                    'bid_size': info.get('bidSize'),
                                    'ask_size': info.get('askSize'),
                                    'tradeable': info.get('tradeable'),
                                    'triggerable': info.get('triggerable'),
                                    'has_pre_post_market_data': info.get('hasPrePostMarketData'),
                                    'pre_market_price': info.get('preMarketPrice'),
                                    'pre_market_change': info.get('preMarketChange'),
                                    'pre_market_change_percent': info.get('preMarketChangePercent'),
                                    'pre_market_time': info.get('preMarketTime'),
                                    'market_state': info.get('marketState'),
                                    'exchange': info.get('exchange'),
                                    'full_exchange_name': info.get('fullExchangeName'),
                                    'quote_source_name': info.get('quoteSourceName'),
                                    'exchange_timezone_name': info.get('exchangeTimezoneName'),
                                    'exchange_timezone_short_name': info.get('exchangeTimezoneShortName'),
                                    'gmt_offset_milliseconds': info.get('gmtOffSetMilliseconds'),
                                    'market': info.get('market'),
                                    'first_trade_date_milliseconds': info.get('firstTradeDateMilliseconds'),
                                    'source_interval': info.get('sourceInterval'),
                                    'exchange_data_delayed_by': info.get('exchangeDataDelayedBy'),
                                    
                                    # Financial Ratios
                                    'trailing_pe': info.get('trailingPE'),
                                    'forward_pe': info.get('forwardPE'),
                                    'price_to_book': info.get('priceToBook'),
                                    'price_to_sales_trailing_12_months': info.get('priceToSalesTrailing12Months'),
                                    'enterprise_to_revenue': info.get('enterpriseToRevenue'),
                                    'enterprise_to_ebitda': info.get('enterpriseToEbitda'),
                                    'trailing_peg_ratio': info.get('trailingPegRatio'),
                                    'price_eps_current_year': info.get('priceEpsCurrentYear'),
                                    'eps_trailing_twelve_months': info.get('epsTrailingTwelveMonths'),
                                    'eps_forward': info.get('epsForward'),
                                    'eps_current_year': info.get('epsCurrentYear'),
                                    
                                    # Dividend Information
                                    'dividend_rate': info.get('dividendRate'),
                                    'dividend_yield': info.get('dividendYield'),
                                    'trailing_annual_dividend_rate': info.get('trailingAnnualDividendRate'),
                                    'trailing_annual_dividend_yield': info.get('trailingAnnualDividendYield'),
                                    'five_year_avg_dividend_yield': info.get('fiveYearAvgDividendYield'),
                                    'payout_ratio': info.get('payoutRatio'),
                                    'last_dividend_value': info.get('lastDividendValue'),
                                    'last_dividend_date': info.get('lastDividendDate'),
                                    'ex_dividend_date': info.get('exDividendDate'),
                                    'dividend_date': info.get('dividendDate'),
                                    
                                    # Shares Information
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
                                    'implied_shares_outstanding': info.get('impliedSharesOutstanding'),
                                    
                                    # Financial Metrics
                                    'beta': info.get('beta'),
                                    'book_value': info.get('bookValue'),
                                    'total_cash': info.get('totalCash'),
                                    'total_cash_per_share': info.get('totalCashPerShare'),
                                    'total_debt': info.get('totalDebt'),
                                    'total_revenue': info.get('totalRevenue'),
                                    'net_income_to_common': info.get('netIncomeToCommon'),
                                    'gross_profits': info.get('grossProfits'),
                                    'ebitda': info.get('ebitda'),
                                    'free_cashflow': info.get('freeCashflow'),
                                    'operating_cashflow': info.get('operatingCashflow'),
                                    'revenue_per_share': info.get('revenuePerShare'),
                                    
                                    # Growth and Margins
                                    'earnings_growth': info.get('earningsGrowth'),
                                    'revenue_growth': info.get('revenueGrowth'),
                                    'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth'),
                                    'gross_margins': info.get('grossMargins'),
                                    'profit_margins': info.get('profitMargins'),
                                    'operating_margins': info.get('operatingMargins'),
                                    'ebitda_margins': info.get('ebitdaMargins'),
                                    
                                    # Financial Health
                                    'debt_to_equity': info.get('debtToEquity'),
                                    'return_on_assets': info.get('returnOnAssets'),
                                    'return_on_equity': info.get('returnOnEquity'),
                                    'quick_ratio': info.get('quickRatio'),
                                    'current_ratio': info.get('currentRatio'),
                                    
                                    # Analyst Recommendations
                                    'target_high_price': info.get('targetHighPrice'),
                                    'target_low_price': info.get('targetLowPrice'),
                                    'target_mean_price': info.get('targetMeanPrice'),
                                    'target_median_price': info.get('targetMedianPrice'),
                                    'recommendation_mean': info.get('recommendationMean'),
                                    'recommendation_key': info.get('recommendationKey'),
                                    'average_analyst_rating': info.get('averageAnalystRating'),
                                    'number_of_analyst_opinions': info.get('numberOfAnalystOpinions'),
                                    
                                    # Risk Metrics
                                    'audit_risk': info.get('auditRisk'),
                                    'board_risk': info.get('boardRisk'),
                                    'compensation_risk': info.get('compensationRisk'),
                                    'share_holder_rights_risk': info.get('shareHolderRightsRisk'),
                                    'overall_risk': info.get('overallRisk'),
                                    
                                    # Dates and Timestamps
                                    'governance_epoch_date': info.get('governanceEpochDate'),
                                    'compensation_as_of_epoch_date': info.get('compensationAsOfEpochDate'),
                                    'last_fiscal_year_end': info.get('lastFiscalYearEnd'),
                                    'next_fiscal_year_end': info.get('nextFiscalYearEnd'),
                                    'most_recent_quarter': info.get('mostRecentQuarter'),
                                    'earnings_timestamp': info.get('earningsTimestamp'),
                                    'earnings_timestamp_start': info.get('earningsTimestampStart'),
                                    'earnings_timestamp_end': info.get('earningsTimestampEnd'),
                                    'earnings_call_timestamp_start': info.get('earningsCallTimestampStart'),
                                    'earnings_call_timestamp_end': info.get('earningsCallTimestampEnd'),
                                    'is_earnings_date_estimate': info.get('isEarningsDateEstimate'),
                                    
                                    # Additional Fields
                                    'currency': info.get('currency'),
                                    'financial_currency': info.get('financialCurrency'),
                                    'quote_type': info.get('quoteType'),
                                    'message_board_id': info.get('messageBoardId'),
                                    'corporate_actions': info.get('corporateActions'),
                                    'executive_team': info.get('executiveTeam'),
                                    'company_officers': info.get('companyOfficers'),
                                    'custom_price_alert_confidence': info.get('customPriceAlertConfidence'),
                                    'esg_populated': info.get('esgPopulated'),
                                    'cryptoTradeable': info.get('cryptoTradeable'),
                                    'max_age': info.get('maxAge'),
                                    
                                    # Additional fields that might exist
                                    'last_split_factor': info.get('lastSplitFactor'),
                                    'last_split_date': info.get('lastSplitDate'),
                                    'ir_website': info.get('irWebsite'),
                                    'corporate_actions': info.get('corporateActions'),
                                    'executive_team': info.get('executiveTeam'),
                                    'company_officers': info.get('companyOfficers'),
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
                            ticker_data = self._get_single_ticker_info(ticker)
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
    
    def _get_single_ticker_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get data for a single ticker (fallback method)"""
        try:
            self.logger.info(f"Fetching data for {ticker} via yfinance API...")
            
            # Create ticker object
            if self.session:
                ticker_obj = yf.Ticker(ticker, session=self.session)
            else:
                ticker_obj = yf.Ticker(ticker)
            
            # Get basic info - this contains all the data we need
            info = ticker_obj.info
            
            # Compile all data from info object using the same comprehensive structure
            ticker_data = {
                'ticker': ticker,
                'scraped_at': datetime.now().isoformat(),
                'data': {
                    # Company Information
                    'long_name': info.get('longName'),
                    'short_name': info.get('shortName'),
                    'long_business_summary': info.get('longBusinessSummary'),
                    'website': info.get('website'),
                    'phone': info.get('phone'),
                    'address1': info.get('address1'),
                    'city': info.get('city'),
                    'state': info.get('state'),
                    'zip': info.get('zip'),
                    'country': info.get('country'),
                    'full_time_employees': info.get('fullTimeEmployees'),
                    'industry': info.get('industry'),
                    'industry_key': info.get('industryKey'),
                    'industry_disp': info.get('industryDisp'),
                    'sector': info.get('sector'),
                    'sector_key': info.get('sectorKey'),
                    'sector_disp': info.get('sectorDisp'),
                    'ir_website': info.get('irWebsite'),
                    'language': info.get('language'),
                    'region': info.get('region'),
                    'type_disp': info.get('typeDisp'),
                    'display_name': info.get('displayName'),
                    'symbol': info.get('symbol'),
                    
                    # Market Data
                    'market_cap': info.get('marketCap'),
                    'enterprise_value': info.get('enterpriseValue'),
                    'current_price': info.get('currentPrice'),
                    'regular_market_price': info.get('regularMarketPrice'),
                    'previous_close': info.get('previousClose'),
                    'open': info.get('open'),
                    'day_low': info.get('dayLow'),
                    'day_high': info.get('dayHigh'),
                    'regular_market_open': info.get('regularMarketOpen'),
                    'regular_market_day_low': info.get('regularMarketDayLow'),
                    'regular_market_day_high': info.get('regularMarketDayHigh'),
                    'regular_market_previous_close': info.get('regularMarketPreviousClose'),
                    'regular_market_change': info.get('regularMarketChange'),
                    'regular_market_change_percent': info.get('regularMarketChangePercent'),
                    'regular_market_day_range': info.get('regularMarketDayRange'),
                    'regular_market_time': info.get('regularMarketTime'),
                    'regular_market_volume': info.get('regularMarketVolume'),
                    'volume': info.get('volume'),
                    'average_volume': info.get('averageVolume'),
                    'average_volume_10days': info.get('averageVolume10days'),
                    'average_daily_volume_10_day': info.get('averageDailyVolume10Day'),
                    'average_daily_volume_3_month': info.get('averageDailyVolume3Month'),
                    
                    # Price Data
                    'price_hint': info.get('priceHint'),
                    'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                    'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                    'fifty_two_week_low_change': info.get('fiftyTwoWeekLowChange'),
                    'fifty_two_week_low_change_percent': info.get('fiftyTwoWeekLowChangePercent'),
                    'fifty_two_week_high_change': info.get('fiftyTwoWeekHighChange'),
                    'fifty_two_week_high_change_percent': info.get('fiftyTwoWeekHighChangePercent'),
                    'fifty_two_week_range': info.get('fiftyTwoWeekRange'),
                    'fifty_two_week_change_percent': info.get('fiftyTwoWeekChangePercent'),
                    'fifty_day_average': info.get('fiftyDayAverage'),
                    'fifty_day_average_change': info.get('fiftyDayAverageChange'),
                    'fifty_day_average_change_percent': info.get('fiftyDayAverageChangePercent'),
                    'two_hundred_day_average': info.get('twoHundredDayAverage'),
                    'two_hundred_day_average_change': info.get('twoHundredDayAverageChange'),
                    'two_hundred_day_average_change_percent': info.get('twoHundredDayAverageChangePercent'),
                    'sandp_52_week_change': info.get('SandP52WeekChange'),
                    
                    # Trading Information
                    'bid': info.get('bid'),
                    'ask': info.get('ask'),
                    'bid_size': info.get('bidSize'),
                    'ask_size': info.get('askSize'),
                    'tradeable': info.get('tradeable'),
                    'triggerable': info.get('triggerable'),
                    'has_pre_post_market_data': info.get('hasPrePostMarketData'),
                    'pre_market_price': info.get('preMarketPrice'),
                    'pre_market_change': info.get('preMarketChange'),
                    'pre_market_change_percent': info.get('preMarketChangePercent'),
                    'pre_market_time': info.get('preMarketTime'),
                    'market_state': info.get('marketState'),
                    'exchange': info.get('exchange'),
                    'full_exchange_name': info.get('fullExchangeName'),
                    'quote_source_name': info.get('quoteSourceName'),
                    'exchange_timezone_name': info.get('exchangeTimezoneName'),
                    'exchange_timezone_short_name': info.get('exchangeTimezoneShortName'),
                    'gmt_offset_milliseconds': info.get('gmtOffSetMilliseconds'),
                    'market': info.get('market'),
                    'first_trade_date_milliseconds': info.get('firstTradeDateMilliseconds'),
                    'source_interval': info.get('sourceInterval'),
                    'exchange_data_delayed_by': info.get('exchangeDataDelayedBy'),
                    
                    # Financial Ratios
                    'trailing_pe': info.get('trailingPE'),
                    'forward_pe': info.get('forwardPE'),
                    'price_to_book': info.get('priceToBook'),
                    'price_to_sales_trailing_12_months': info.get('priceToSalesTrailing12Months'),
                    'enterprise_to_revenue': info.get('enterpriseToRevenue'),
                    'enterprise_to_ebitda': info.get('enterpriseToEbitda'),
                    'trailing_peg_ratio': info.get('trailingPegRatio'),
                    'price_eps_current_year': info.get('priceEpsCurrentYear'),
                    'eps_trailing_twelve_months': info.get('epsTrailingTwelveMonths'),
                    'eps_forward': info.get('epsForward'),
                    'eps_current_year': info.get('epsCurrentYear'),
                    
                    # Dividend Information
                    'dividend_rate': info.get('dividendRate'),
                    'dividend_yield': info.get('dividendYield'),
                    'trailing_annual_dividend_rate': info.get('trailingAnnualDividendRate'),
                    'trailing_annual_dividend_yield': info.get('trailingAnnualDividendYield'),
                    'five_year_avg_dividend_yield': info.get('fiveYearAvgDividendYield'),
                    'payout_ratio': info.get('payoutRatio'),
                    'last_dividend_value': info.get('lastDividendValue'),
                    'last_dividend_date': info.get('lastDividendDate'),
                    'ex_dividend_date': info.get('exDividendDate'),
                    'dividend_date': info.get('dividendDate'),
                    
                    # Shares Information
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
                    'implied_shares_outstanding': info.get('impliedSharesOutstanding'),
                    
                    # Financial Metrics
                    'beta': info.get('beta'),
                    'book_value': info.get('bookValue'),
                    'total_cash': info.get('totalCash'),
                    'total_cash_per_share': info.get('totalCashPerShare'),
                    'total_debt': info.get('totalDebt'),
                    'total_revenue': info.get('totalRevenue'),
                    'net_income_to_common': info.get('netIncomeToCommon'),
                    'gross_profits': info.get('grossProfits'),
                    'ebitda': info.get('ebitda'),
                    'free_cashflow': info.get('freeCashflow'),
                    'operating_cashflow': info.get('operatingCashflow'),
                    'revenue_per_share': info.get('revenuePerShare'),
                    
                    # Growth and Margins
                    'earnings_growth': info.get('earningsGrowth'),
                    'revenue_growth': info.get('revenueGrowth'),
                    'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth'),
                    'gross_margins': info.get('grossMargins'),
                    'profit_margins': info.get('profitMargins'),
                    'operating_margins': info.get('operatingMargins'),
                    'ebitda_margins': info.get('ebitdaMargins'),
                    
                    # Financial Health
                    'debt_to_equity': info.get('debtToEquity'),
                    'return_on_assets': info.get('returnOnAssets'),
                    'return_on_equity': info.get('returnOnEquity'),
                    'quick_ratio': info.get('quickRatio'),
                    'current_ratio': info.get('currentRatio'),
                    
                    # Analyst Recommendations
                    'target_high_price': info.get('targetHighPrice'),
                    'target_low_price': info.get('targetLowPrice'),
                    'target_mean_price': info.get('targetMeanPrice'),
                    'target_median_price': info.get('targetMedianPrice'),
                    'recommendation_mean': info.get('recommendationMean'),
                    'recommendation_key': info.get('recommendationKey'),
                    'average_analyst_rating': info.get('averageAnalystRating'),
                    'number_of_analyst_opinions': info.get('numberOfAnalystOpinions'),
                    
                    # Risk Metrics
                    'audit_risk': info.get('auditRisk'),
                    'board_risk': info.get('boardRisk'),
                    'compensation_risk': info.get('compensationRisk'),
                    'share_holder_rights_risk': info.get('shareHolderRightsRisk'),
                    'overall_risk': info.get('overallRisk'),
                    
                    # Dates and Timestamps
                    'governance_epoch_date': info.get('governanceEpochDate'),
                    'compensation_as_of_epoch_date': info.get('compensationAsOfEpochDate'),
                    'last_fiscal_year_end': info.get('lastFiscalYearEnd'),
                    'next_fiscal_year_end': info.get('nextFiscalYearEnd'),
                    'most_recent_quarter': info.get('mostRecentQuarter'),
                    'earnings_timestamp': info.get('earningsTimestamp'),
                    'earnings_timestamp_start': info.get('earningsTimestampStart'),
                    'earnings_timestamp_end': info.get('earningsTimestampEnd'),
                    'earnings_call_timestamp_start': info.get('earningsCallTimestampStart'),
                    'earnings_call_timestamp_end': info.get('earningsCallTimestampEnd'),
                    'is_earnings_date_estimate': info.get('isEarningsDateEstimate'),
                    
                    # Additional Fields
                    'currency': info.get('currency'),
                    'financial_currency': info.get('financialCurrency'),
                    'quote_type': info.get('quoteType'),
                    'message_board_id': info.get('messageBoardId'),
                    'corporate_actions': info.get('corporateActions'),
                    'executive_team': info.get('executiveTeam'),
                    'company_officers': info.get('companyOfficers'),
                    'custom_price_alert_confidence': info.get('customPriceAlertConfidence'),
                    'esg_populated': info.get('esgPopulated'),
                    'cryptoTradeable': info.get('cryptoTradeable'),
                    'max_age': info.get('maxAge'),
                    
                    # Additional fields that might exist
                    'last_split_factor': info.get('lastSplitFactor'),
                    'last_split_date': info.get('lastSplitDate'),
                    'ir_website': info.get('irWebsite'),
                }
            }
            
            self.logger.info(f"Successfully fetched data for {ticker}")
            return ticker_data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {ticker}: {str(e)}")
            return None
