# Railway Deployment Guide

This guide explains how to deploy the `api_to_database.py` script to Railway to run once every day.

## What This Deployment Does

- Runs `python api_to_database.py -b 15 --skip-existing --hours-window 24` daily at 9:00 AM UTC
- **Smart Filtering**: Only processes tickers without data in the last 24 hours
- **Batch Processing**: Processes ticker data in batches of 15
- **Error Handling**: Improved handling of numeric overflow and infinite values
- **Database Schema**: Enhanced schema with larger precision fields
- Saves data to your Nhost database
- Provides comprehensive logging and error handling

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Git Repository**: Your code should be in a Git repository
3. **Environment Variables**: Set up your database credentials in Railway

## Deployment Steps

### 1. Connect Your Repository

```bash
# In Railway dashboard, click "New Project" → "Deploy from GitHub repo"
# Select your repository
```

### 2. Set Environment Variables

In Railway dashboard, go to your project → Variables tab and add:

```bash
# Database connection (Nhost)
NHOST_GRAPHQL_URL=your_nhost_graphql_url
NHOST_GRAPHQL_ADMIN_SECRET=your_admin_secret

# Optional: Logging level
LOG_LEVEL=INFO
```

### 3. Deploy

Railway will automatically:
- Build your project using Nixpacks
- Install dependencies from `requirements.txt`
- Run the deployment script

### 4. Verify Deployment

Check the Railway logs to ensure:
- ✅ Script executed successfully
- ✅ Database connection established
- ✅ Ticker data processed

## Time-Based Filtering Options

The deployment now includes smart filtering to avoid reprocessing tickers with recent data:

### Default Behavior (24 hours)
- **`--skip-existing`**: Skips tickers with data in the last 24 hours
- **`--hours-window 24`**: Configurable time window (default: 24 hours)

### Custom Time Windows
```bash
# Process tickers without data in last 6 hours
python api_to_database.py -s -hw 6

# Process tickers without data in last 12 hours  
python api_to_database.py -s -hw 12

# Process tickers without data in last 48 hours
python api_to_database.py -s -hw 48

# Process tickers without data in last week
python api_to_database.py -s -hw 168
```

### Benefits
- **Efficient**: Only processes tickers that need updating
- **Flexible**: Adjust time windows based on your needs
- **Database Friendly**: Reduces unnecessary database operations
- **Cost Effective**: Minimizes API calls and processing time

## Configuration Files

- **`railway.json`**: Main Railway configuration
- **`railway_deploy.py`**: Deployment wrapper script
- **`Procfile`**: Process definition for Railway
- **`.railwayignore`**: Files to exclude from deployment

## Cron Schedule

The script runs daily at **9:00 AM UTC** using the cron expression: `0 9 * * *`

You can modify this in `railway.json` if you need a different schedule.

## Monitoring

### View Logs
- Railway dashboard → Your project → Deployments → View logs
- Check `railway_deploy.log` in the application

### Check Execution
- Monitor database for new ticker data
- Verify logs show successful processing

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify environment variables are set correctly
   - Check Nhost service status

2. **Script Timeout**
   - Default timeout is 1 hour
   - Increase if processing large numbers of tickers

3. **Dependencies Missing**
   - Ensure `requirements.txt` includes all needed packages
   - Check build logs for installation errors

4. **Numeric Overflow Errors**
   - Run `python reset_database.py` to recreate tables with new schema
   - New schema handles larger numbers and infinite values better

### Debug Mode

To test locally before deploying:

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Test the deployment script
python railway_deploy.py

# Test the main script directly
python api_to_database.py -b 15 --skip-existing

# Test time filtering
python test_time_filtering.py
```

## Customization

### Change Batch Size
Modify the command in `railway_deploy.py`:
```python
cmd = ["python", "api_to_database.py", "-b", "20", "--skip-existing", "--hours-window", "24"]
```

### Change Schedule
Modify the cron expression in `railway.json`:
```json
"cron": {
  "schedule": "0 12 * * *",  # Run at 12:00 PM UTC instead
  "command": "python railway_deploy.py"
}
```

### Change Time Window
Modify the hours window in `railway_deploy.py`:
```python
cmd = ["python", "api_to_database.py", "-b", "15", "--skip-existing", "--hours-window", "48"]
```

## Security Notes

- Never commit sensitive credentials to Git
- Use Railway's environment variables for secrets
- Consider using Railway's built-in secrets management

## Support

If you encounter issues:
1. Check Railway logs first
2. Verify environment variables
3. Test locally with the same configuration
4. Check Railway status page for service issues
5. Run `python reset_database.py` if you get numeric overflow errors