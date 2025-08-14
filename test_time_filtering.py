#!/usr/bin/env python3
"""
Test script to demonstrate the new time-based filtering functionality
"""

import logging
from api_to_database import APIToDatabaseBridge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_time_filtering():
    """Test different time window filtering options"""
    
    print("🧪 Testing Time-Based Filtering Functionality")
    print("=" * 60)
    
    # Initialize the bridge
    bridge = APIToDatabaseBridge(use_database=True)
    
    if not bridge.use_db:
        print("❌ Database not available - cannot test filtering")
        return
    
    # Test different time windows
    time_windows = [6, 12, 24, 48, 168]  # 6h, 12h, 24h, 48h, 1 week
    
    for hours in time_windows:
        print(f"\n⏰ Testing {hours}-hour window:")
        print("-" * 40)
        
        try:
            # Get tickers without recent data
            tickers = bridge.get_tickers_from_file(
                filename='all_tickers_api.txt',
                count=50,  # Limit to 50 for testing
                skip_existing=True,
                hours_window=hours
            )
            
            print(f"✅ Found {len(tickers)} tickers without data in last {hours} hours")
            if tickers:
                print(f"📊 Sample tickers: {', '.join(tickers[:10])}")
            
        except Exception as e:
            print(f"❌ Error testing {hours}-hour window: {e}")
    
    print("\n🎯 Testing Complete!")
    print("\n💡 Usage Examples:")
    print("  python api_to_database.py -s -hw 6     # Process tickers without data in last 6 hours")
    print("  python api_to_database.py -s -hw 12    # Process tickers without data in last 12 hours")
    print("  python api_to_database.py -s -hw 24    # Process tickers without data in last 24 hours (default)")
    print("  python api_to_database.py -s -hw 48    # Process tickers without data in last 48 hours")
    print("  python api_to_database.py -s -hw 168   # Process tickers without data in last week")

if __name__ == "__main__":
    test_time_filtering()
