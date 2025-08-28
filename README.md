# 🚀 Yahoo Finance Manager

A comprehensive stock data management application with automated scraping, FastAPI backend, and React frontend.

## 📁 **New Professional Project Structure**

```
yahoof/
├── frontend/                    # 🎨 React Frontend (Phase 2 Complete)
│   ├── src/
│   │   ├── components/         # React Components
│   │   │   ├── common/         # Shared components
│   │   │   ├── layout/         # Layout components
│   │   │   ├── pages/          # Page components
│   │   │   └── ui/             # Reusable UI components
│   │   ├── constants/          # App-wide constants
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # API services
│   │   ├── types/              # TypeScript definitions
│   │   ├── utils/              # Utility functions
│   │   └── assets/             # Static assets
│   └── package.json
├── backend/                     # ⚙️ FastAPI Backend (Phase 1 Complete)
│   ├── api/                    # API endpoints
│   │   └── main_api.py        # Main FastAPI application
│   ├── core/                   # Core functionality
│   │   ├── database.py        # Database configuration
│   │   └── db_manager_sqlalchemy.py  # Database manager
│   ├── models/                 # Database models
│   │   └── models_simple.py   # SQLAlchemy ORM models
│   ├── scripts/                # Scraping scripts
│   │   ├── yfinance_api_scraper.py      # Yahoo Finance scraper
│   │   └── parallel_scrape_sqlalchemy.py # Parallel scraping
│   ├── config/                 # Configuration
│   │   └── settings.py        # Centralized settings
│   ├── utils/                  # Utility functions
│   │   └── helpers.py         # Helper utilities
│   ├── tests/                  # Test files
│   ├── main.py                 # Main entry point
│   └── requirements.txt        # Python dependencies
├── venv/                       # Python virtual environment
├── .env                        # Environment variables
├── requirements.txt            # Root requirements
└── README.md                   # This file
```

## 🎯 **Implementation Status**

### ✅ **Phase 0: SQLAlchemy Migration (COMPLETE)**
- Migrated from old `DatabaseManager` to SQLAlchemy ORM
- Updated all database operations to use SQLAlchemy
- Fixed ScrapingBee integration issues
- Comprehensive testing completed

### ✅ **Phase 1: FastAPI Backend (COMPLETE)**
- Complete REST API with all endpoints
- SQLAlchemy integration
- CORS configuration for frontend
- Comprehensive error handling
- API documentation with Swagger UI

### ✅ **Phase 2: React Frontend (COMPLETE)**
- Modern React 18 with TypeScript
- Tailwind CSS for styling
- Responsive design with mobile support
- Complete component library
- API integration with FastAPI backend

### 🔄 **Phase 3: Railway Deployment (NEXT)**
- Deploy backend to Railway
- Configure production database
- Set up environment variables
- Deploy frontend to Railway

### 📋 **Phase 4: Scraper Automation (PLANNED)**
- Railway cron jobs
- Automated scraper execution
- Database-driven scraper configuration
- Monitoring and alerting

## 🚀 **Quick Start**

### **Backend Setup**
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r ../requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run the FastAPI server
python main.py
# or
uvicorn api.main_api:app --host 0.0.0.0 --port 8000 --reload
```

### **Frontend Setup**
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### **Database Setup**
```bash
# Create database tables
cd backend
python -c "from core.database import create_tables; create_tables()"
```

## 🔧 **Key Features**

### **Backend (FastAPI)**
- **RESTful API**: Complete CRUD operations for stocks, tickers, and scrapers
- **SQLAlchemy ORM**: Modern database operations with connection pooling
- **Scraping Engine**: Yahoo Finance integration with ScrapingBee proxy support
- **Parallel Processing**: Multi-worker scraping with configurable batch sizes
- **Configuration Management**: Centralized settings with environment variable support

### **Frontend (React)**
- **Dashboard**: Overview statistics and recent activity
- **Stock Management**: Browse, filter, and paginate stock data
- **Scraper Management**: Create, configure, and monitor scrapers
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Type Safety**: Full TypeScript implementation

### **Scraping System**
- **Yahoo Finance Integration**: Real-time stock data collection
- **Proxy Support**: ScrapingBee integration for rate limit avoidance
- **Batch Processing**: Efficient parallel scraping with configurable workers
- **Data Persistence**: Automatic database storage and updates

## 🌐 **API Endpoints**

### **Health & Status**
- `GET /health` - API health check

### **Stocks**
- `GET /api/stocks` - Get paginated stock data with filtering
- `GET /api/stocks/{ticker}` - Get specific stock details
- `GET /api/stocks/{ticker}/history` - Get stock price history

### **Tickers**
- `GET /api/tickers` - Get paginated ticker information

### **Scrapers**
- `GET /api/scrapers` - List all scrapers
- `POST /api/scrapers` - Create new scraper
- `PUT /api/scrapers/{id}` - Update scraper
- `DELETE /api/scrapers/{id}` - Delete scraper
- `POST /api/scrapers/{id}/run` - Execute scraper

### **Statistics**
- `GET /api/stats/overview` - Dashboard overview statistics

## 🗄️ **Database Schema**

### **Tables**
- **`scraped_data`**: Stock price and company information
- **`tickers`**: Ticker metadata and company details
- **`scrapers`**: Scraper configuration and scheduling
- **`scraper_runs`**: Execution history and results

## 🔐 **Environment Variables**

### **Required**
```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

### **Optional**
```bash
SCRAPINGBEE_API_KEY=your_api_key_here
API_DEBUG=False
LOG_LEVEL=INFO
```

## 🧪 **Testing**

### **Backend Testing**
```bash
cd backend
python -m pytest tests/
```

### **Frontend Testing**
```bash
cd frontend
npm test
```

## 📊 **Performance**

### **Scraping Performance**
- **Parallel Workers**: Configurable (default: 4)
- **Batch Size**: Configurable (default: 10)
- **Rate Limiting**: Built-in delays and ScrapingBee proxy support
- **Database Optimization**: Connection pooling and efficient queries

### **API Performance**
- **Response Time**: < 100ms for most endpoints
- **Pagination**: Efficient database queries with LIMIT/OFFSET
- **Caching**: Ready for Redis integration
- **Async Support**: Full async/await implementation

## 🚀 **Deployment**

### **Railway (Recommended)**
- **Backend**: Python FastAPI with PostgreSQL
- **Frontend**: React static build
- **Database**: Managed PostgreSQL
- **Cron Jobs**: Automated scraper execution

### **Local Development**
- **Backend**: `python backend/main.py`
- **Frontend**: `npm start` in frontend directory
- **Database**: Local PostgreSQL instance

## 🔮 **Future Enhancements**

### **Phase 5: Advanced Features**
- **Real-time Updates**: WebSocket integration
- **Advanced Analytics**: Chart.js integration
- **User Authentication**: JWT-based auth system
- **Data Export**: CSV/Excel export functionality
- **Email Notifications**: Scraper status alerts

### **Phase 6: Enterprise Features**
- **Multi-tenant Support**: Organization-based data isolation
- **API Rate Limiting**: Advanced request throttling
- **Audit Logging**: Complete action tracking
- **Backup & Recovery**: Automated data protection
- **Monitoring Dashboard**: System health metrics

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License.

---

**Built with ❤️ using FastAPI, React, SQLAlchemy, and Tailwind CSS**

**Current Status: Frontend & Backend Complete - Ready for Railway Deployment! 🎉** 