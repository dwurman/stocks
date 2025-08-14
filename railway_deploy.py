#!/usr/bin/env python3
"""
Railway deployment script for api_to_database.py
This script runs once when deployed and executes the main script with the specified parameters
"""

import os
import sys
import logging
from datetime import datetime
import subprocess

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('railway_deploy.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main deployment function"""
    try:
        logger.info("🚀 Starting Railway deployment of api_to_database.py")
        logger.info(f"⏰ Deployment time: {datetime.now()}")
        logger.info(f"🔧 Python version: {sys.version}")
        logger.info(f"📁 Working directory: {os.getcwd()}")
        
        # Check if we're in Railway environment
        if os.getenv('RAILWAY_ENVIRONMENT'):
            logger.info("✅ Running in Railway environment")
        else:
            logger.info("⚠️ Not running in Railway environment")
        
        # Set the command to run
        cmd = ["python", "api_to_database.py", "-b", "15", "--skip-existing", "--hours-window", "24"]
        logger.info(f"🎯 Executing command: {' '.join(cmd)}")
        
        # Execute the main script
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        # Log the results
        if result.stdout:
            logger.info("📤 Script output:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    logger.info(f"  {line}")
        
        if result.stderr:
            logger.warning("⚠️ Script errors/warnings:")
            for line in result.stderr.strip().split('\n'):
                if line.strip():
                    logger.warning(f"  {line}")
        
        # Check exit code
        if result.returncode == 0:
            logger.info("✅ Script executed successfully")
        else:
            logger.error(f"❌ Script failed with exit code: {result.returncode}")
        
        logger.info("🏁 Railway deployment completed")
        
    except subprocess.TimeoutExpired:
        logger.error("⏰ Script execution timed out after 1 hour")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error during deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
