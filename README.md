# Yahoo Finance API Scraper

A simplified Yahoo Finance API scraper that downloads stock data in batches and saves it to a PostgreSQL database.

## Features

- **Batch Processing**: Downloads data for multiple tickers efficiently using yfinance batch functionality
- **Database Integration**: Saves data to PostgreSQL database with tables for `scraped_data` and `tickers`
- **Comprehensive Data**: Captures company information, market data, financial ratios, and more
- **Error Handling**: Robust error handling with fallback mechanisms

## Requirements

- Python 3.7+
- PostgreSQL database
- Required packages (see `requirements.txt`)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   NHOST_URL=your_postgresql_host
   NHOST_ADMIN_SECRET=your_database_password
   ```

## Usage

### Basic Usage

```python
from yfinance_api_scraper import YahooFinanceAPIScraper
from db_module import DatabaseManager

# Initialize scraper and database
scraper = YahooFinanceAPIScraper()
db = DatabaseManager()

# Download data for multiple tickers
tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
data = scraper.get_batch_tickers_info(tickers, batch_size=3)

# Save to database
db.save_batch_ticker_data(data)
```

### Run the Example

```bash
python main.py
```

## Database Schema

### scraped_data Table
Stores the main financial data for each ticker including:
- Company information (name, sector, industry, etc.)
- Market data (price, volume, market cap, etc.)
- Financial ratios (PE, PB, debt-to-equity, etc.)
- Growth metrics and additional financial data

### tickers Table
Stores metadata about each ticker including:
- Ticker symbol and company name
- Exchange, industry, sector, country
- Scraping status and timestamps

## Configuration

The scraper automatically handles:
- Batch processing with configurable batch sizes
- Rate limiting and API respect
- Fallback mechanisms for failed requests
- Data cleaning and validation

## Error Handling

- Graceful fallback to individual ticker fetching if batch fails
- Comprehensive logging for debugging
- Database connection fallback mode for development
- Data validation and cleaning before database insertion 