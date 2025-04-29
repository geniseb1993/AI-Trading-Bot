#!/usr/bin/env python
"""
Test Market Data Fix

This script tests the market data endpoint fix to verify it's working correctly.
"""

import requests
import json
import sys

def test_health_endpoint():
    """Test the health endpoint to ensure the server is running."""
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:5000/api/health")
        if response.status_code == 200:
            print("✅ Health endpoint is working")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health endpoint returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")
        return False

def test_market_data_endpoint():
    """Test the market data endpoint for SPY."""
    print("\nTesting market data endpoint for SPY...")
    try:
        response = requests.get("http://localhost:5000/api/market-data/SPY")
        if response.status_code == 200:
            data = response.json()
            print("✅ Market data endpoint is working")
            print(f"Symbol: {data.get('symbol')}")
            print(f"Timeframe: {data.get('timeframe')}")
            print(f"Days: {data.get('days')}")
            print(f"Using real data: {data.get('isRealData', False)}")
            print(f"Data source: {data.get('source', 'unknown')}")
            print(f"Number of bars: {len(data.get('bars', []))}")
            
            # Check if we have bars
            if len(data.get('bars', [])) > 0:
                print("\nSample bar data:")
                sample_bar = data.get('bars', [])[0]
                for key, value in sample_bar.items():
                    print(f"  {key}: {value}")
            
            return True
        else:
            print(f"❌ Market data endpoint returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing market data endpoint: {e}")
        return False

def main():
    """Run the tests."""
    print("=== Market Data Fix Test ===\n")
    
    # Test health endpoint
    if not test_health_endpoint():
        print("\n❌ Health endpoint test failed. Aborting.")
        sys.exit(1)
    
    # Test market data endpoint
    if not test_market_data_endpoint():
        print("\n❌ Market data endpoint test failed.")
        sys.exit(1)
    
    print("\n✅ All tests passed! The market data endpoint fix is working correctly.")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 