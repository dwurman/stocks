# YFinance API Debug Guide

## 🚀 Available Debug Scripts

### 1. **`simple_debug.py`** - Interactive Debugging
**Best for: Setting breakpoints and exploring in debug console**

```bash
./venv/Scripts/python.exe simple_debug.py
```

**How to use:**
1. Open `simple_debug.py` in your IDE
2. Set a breakpoint on the line: `debug_point = True`
3. Run in debug mode
4. Use debug console to explore variables

**Available variables in debug session:**
- `ticker` - String ticker symbol ('AAPL')
- `stock` - yf.Ticker object for AAPL
- `info` - Dictionary with 180+ data fields
- `batch` - yf.Tickers object for multiple stocks
- `hist` - Historical price data DataFrame

### 2. **`debug_yfinance.py`** - Comprehensive Explorer
**Best for: Understanding API structure and capabilities**

```bash
./venv/Scripts/python.exe debug_yfinance.py
```

**Available functions:**
- `explore_single_ticker('SYMBOL')` - Deep dive into one stock
- `explore_batch_tickers(['A', 'B'])` - Test batch functionality  
- `explore_historical_data('SYMBOL')` - Price history
- `explore_financials('SYMBOL')` - Financial statements
- `explore_info_categories('SYMBOL')` - Categorize all data fields
- `save_sample_data('SYMBOL')` - Export data to JSON

### 3. **`explore_api.py`** - Full Analysis
**Best for: Complete API exploration and data export**

```bash
./venv/Scripts/python.exe explore_api.py
```

## 🔍 Key Discoveries

### **Info Dictionary Structure (180+ fields)**
The `stock.info` dictionary contains:

1. **Company Info (18 fields)**
   - `longName`, `sector`, `industry`, `country`, `website`
   - `longBusinessSummary`, `fullTimeEmployees`

2. **Price Data (28 fields)**
   - `currentPrice`, `previousClose`, `open`, `dayHigh`, `dayLow`
   - `fiftyTwoWeekHigh`, `fiftyTwoWeekLow`
   - `targetHighPrice`, `targetLowPrice`, `targetMeanPrice`

3. **Market Data (25 fields)**
   - `marketCap`, `enterpriseValue`, `volume`, `averageVolume`
   - `sharesOutstanding`, `floatShares`, `sharesShort`

4. **Financial Ratios (36 fields)**
   - `trailingPE`, `forwardPE`, `priceToBook`, `dividendYield`
   - `debtToEquity`, `returnOnEquity`, `profitMargins`

5. **Trading Info (9 fields)**
   - `bid`, `ask`, `bidSize`, `askSize`

### **Batch Processing**
```python
# Single ticker
stock = yf.Ticker('AAPL')
info = stock.info

# Batch tickers (more efficient)
batch = yf.Tickers('AAPL MSFT GOOGL')
apple_info = batch.tickers['AAPL'].info
microsoft_info = batch.tickers['MSFT'].info
```

### **Historical Data**
```python
# Different time periods
hist_1mo = stock.history(period='1mo')    # 22 days
hist_1y = stock.history(period='1y')      # ~252 days
hist_5y = stock.history(period='5y')      # ~1260 days

# Columns: Open, High, Low, Close, Volume, Dividends, Stock Splits
```

### **Financial Statements**
```python
# Available financial data
financials = stock.financials      # Income statement (39 rows x 5 years)
balance_sheet = stock.balance_sheet # Balance sheet (68 rows x 5 years)  
cashflow = stock.cashflow          # Cash flow (53 rows x 5 years)
```

## 🐛 Debug Console Commands

Once you hit a breakpoint in `simple_debug.py`, try these in the debug console:

```python
# Basic exploration
info['longName']
info['currentPrice']
info['marketCap']

# Search for specific fields
[k for k in info.keys() if 'price' in k.lower()]
[k for k in info.keys() if 'volume' in k.lower()]
[k for k in info.keys() if 'ratio' in k.lower()]

# Batch access
batch.tickers['AAPL'].info['longName']
batch.tickers['MSFT'].info['currentPrice']

# Historical data analysis
hist.head()
hist['Close'].mean()
hist['Volume'].max()

# Try different stocks
new_stock = yf.Ticker('GOOGL')
new_info = new_stock.info
new_info['longName']

# Get specific time periods
stock.history(period='5d')
stock.history(period='1mo')
stock.history(period='1y')
```

## 📊 Useful Data Fields

### **Essential Fields for Stock Analysis:**
```python
essential_fields = [
    'longName',           # Company name
    'currentPrice',       # Current stock price
    'marketCap',          # Market capitalization
    'sector',             # Business sector
    'industry',           # Specific industry
    'trailingPE',         # P/E ratio
    'dividendYield',      # Dividend yield
    'volume',             # Current volume
    'averageVolume',      # Average daily volume
    'fiftyTwoWeekHigh',   # 52-week high
    'fiftyTwoWeekLow',    # 52-week low
    'targetMeanPrice',    # Analyst target price
]
```

### **Financial Health Indicators:**
```python
financial_health = [
    'debtToEquity',       # Debt to equity ratio
    'returnOnEquity',     # Return on equity
    'profitMargins',      # Profit margins
    'operatingMargins',   # Operating margins
    'revenueGrowth',      # Revenue growth rate
    'earningsGrowth',     # Earnings growth rate
]
```

## 🎯 Next Steps

1. **Set breakpoints** in `simple_debug.py` to explore interactively
2. **Modify ticker symbols** to explore different stocks
3. **Experiment with batch sizes** for optimal performance
4. **Test error handling** with invalid ticker symbols
5. **Explore historical periods** for different analysis needs

## 📁 Generated Files

- `yfinance_debug_AAPL_*.json` - Complete data export for analysis
- Debug scripts are ready for breakpoint debugging
- Use your IDE's debug console for real-time exploration

Happy debugging! 🐛✨

