# Web Scraper with ScrapingBee and Nhost

A Python web scraping script that uses ScrapingBee for reliable web scraping, BeautifulSoup for HTML parsing, and Nhost for data storage via GraphQL. The script can be scheduled to run daily and deployed on Railway.

## Features

- **Reliable Scraping**: Uses ScrapingBee API to avoid IP blocking and handle complex websites
- **Data Extraction**: BeautifulSoup for parsing HTML and extracting structured data
- **Database Storage**: Nhost integration with GraphQL API for storing scraped data
- **Scheduling**: Built-in scheduling to run daily at 9:00 AM
- **Logging**: Comprehensive logging for monitoring and debugging
- **Railway Ready**: Configured for easy deployment on Railway

## Prerequisites

- Python 3.8+
- ScrapingBee API key
- Nhost account and project
- Railway account (for deployment)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `env.example` to `.env` and fill in your credentials:

```bash
cp env.example .env
```

Edit `.env` with your actual values:

```env
SCRAPINGBEE_API_KEY=your_actual_api_key
NHOST_URL=https://your-project-id.nhost.run
NHOST_ADMIN_SECRET=your_admin_secret
TARGET_URL=https://your-target-website.com
```

### 3. Nhost Setup

1. **Create Nhost Project**:
   - Go to [Nhost](https://nhost.io/) and create a new project
   - Wait for the project to be provisioned

2. **Set up Database Schema**:
   - Go to your Nhost project dashboard
   - Navigate to Hasura Console
   - Go to the SQL Editor
   - Run the contents of `nhost_setup.sql` to create the required table

3. **Get Credentials**:
   - **NHOST_URL**: Your project URL (e.g., `https://abc123.nhost.run`)
   - **NHOST_ADMIN_SECRET**: Found in Settings → API Keys → Admin Secret

### 4. Customize Scraping Logic

Edit the `parse_content` method in `scraper.py` to match your target website's structure:

```python
def parse_content(self, html_content):
    # Modify this method based on your target website
    # Example: Extract articles, products, news, etc.
    pass
```

## Usage

### Local Development

Run the scraper locally:

```bash
python scraper.py
```

The script will:
1. Run immediately once
2. Schedule daily runs at 9:00 AM
3. Continue running until stopped (Ctrl+C)

### Railway Deployment

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize Project**:
   ```bash
   railway init
   ```

4. **Set Environment Variables**:
   ```bash
   railway variables set SCRAPINGBEE_API_KEY=your_key
   railway variables set NHOST_URL=your_nhost_url
   railway variables set NHOST_ADMIN_SECRET=your_admin_secret
   railway variables set TARGET_URL=your_target_url
   ```

5. **Deploy**:
   ```bash
   railway up
   ```

6. **Set up Cron Job** (for daily scheduling):
   - Go to your Railway project dashboard
   - Navigate to Settings → Cron Jobs
   - Add a new cron job:
     - **Schedule**: `0 9 * * *` (daily at 9:00 AM)
     - **Command**: `python scraper.py`

## Configuration Options

### ScrapingBee Parameters

You can modify the ScrapingBee parameters in the `scrape_website` method:

- `render_js`: Set to `true` if JavaScript rendering is needed
- `premium_proxy`: Use premium proxies for better success rate
- `country_code`: Specify proxy country
- `block_ads`: Block advertisements
- `block_resources`: Block certain resource types

### Nhost GraphQL Configuration

The script uses Nhost's GraphQL API with admin privileges. You can modify the GraphQL queries in the `save_to_nhost` method:

```python
# Example: Custom GraphQL query
query = gql("""
    query GetScrapedData {
        scraped_data(limit: 10, order_by: {scraped_at: desc}) {
            id
            title
            scraped_at
        }
    }
""")
```

### Scheduling

Modify the schedule in the `main()` function:

```python
# Run every hour
schedule.every().hour.do(scraper.run_scraping_job)

# Run every Monday at 9:00 AM
schedule.every().monday.at("09:00").do(scraper.run_scraping_job)

# Run every 6 hours
schedule.every(6).hours.do(scraper.run_scraping_job)
```

## Data Structure

The script extracts and stores the following data structure:

```json
{
  "title": "Article Title",
  "link": "https://example.com/article",
  "description": "Article description or summary",
  "timestamp": "2024-01-01T09:00:00",
  "scraped_at": "2024-01-01T09:00:00",
  "source_url": "https://example.com"
}
```

## Monitoring

- **Logs**: Check `scraper.log` for detailed execution logs
- **Railway Dashboard**: Monitor deployment status and logs
- **Nhost Dashboard**: View stored data and monitor database performance
- **Hasura Console**: Query and visualize your data with GraphQL

## Troubleshooting

### Common Issues

1. **ScrapingBee API Errors**: Check your API key and quota
2. **Nhost Connection Issues**: Verify URL and admin secret
3. **GraphQL Errors**: Check table permissions and schema
4. **Parsing Errors**: Customize the `parse_content` method for your website
5. **Scheduling Issues**: Ensure the script stays running (use Railway's restart policy)

### Debug Mode

Enable debug logging by modifying the logging level:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Nhost-Specific Issues

1. **Permission Denied**: Ensure the `hasura` role has proper permissions
2. **Table Not Found**: Run the SQL setup script in Hasura Console
3. **GraphQL Schema Issues**: Check if the table is tracked in Hasura

## Security Considerations

- Never commit `.env` files to version control
- Use admin secrets only in secure environments
- Consider implementing Row Level Security (RLS) policies
- Review and customize Nhost permissions
- Consider implementing rate limiting for large-scale scraping

## License

This project is open source and available under the MIT License.

## Support

For issues related to:
- **ScrapingBee**: Check their [documentation](https://docs.scrapingbee.com/)
- **Nhost**: Visit their [docs](https://docs.nhost.io/)
- **Railway**: Check their [documentation](https://docs.railway.app/) 