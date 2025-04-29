#!/usr/bin/env python
"""
Verify Real Data Configuration
==============================

This script checks that the API server is running and properly returning real data.
"""

import requests
import json
import sys
from datetime import datetime

API_BASE_URL = "http://localhost:5000"

def check_endpoint(endpoint, description, method="GET", json_data=None):
    """Check an endpoint and verify it returns real data"""
    url = f"{API_BASE_URL}{endpoint}"
    print(f"Checking {description} ({url})...")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=json_data, timeout=5)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
            
        response.raise_for_status()
        data = response.json()
        
        # Check if the response contains isRealData flag
        # Look in different locations based on response structure
        is_real = None
        data_source = "Unknown"
        
        if 'isRealData' in data:
            is_real = data['isRealData']
            data_source = data.get('dataSource', data.get('source', 'Unknown'))
        elif 'data' in data and isinstance(data['data'], dict) and 'isRealData' in data['data']:
            is_real = data['data']['isRealData']
            data_source = data['data'].get('dataSource', 'Unknown')
            
        if is_real is not None and is_real:
            print(f"✅ {description} is returning REAL data from {data_source}")
            return True
        elif is_real is not None and not is_real:
            print(f"❌ {description} is NOT returning real data (using {data_source})")
            return False
        else:
            print(f"❌ {description} does not have isRealData flag in expected location")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error checking {description}: {str(e)}")
        return False

def main():
    """Main function to check all endpoints"""
    print("===========================================")
    print("Real Data Verification Tool")
    print("===========================================")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("Checking API server endpoints...\n")
    
    # List of endpoints to check
    endpoints = [
        ("/api/status", "API Status", "GET", None),
        ("/api/institutional-flow/get-data", "Institutional Flow", "POST", {"type": "options-flow", "timeframe": "today"}),
        ("/api/bot/status", "Bot Status", "GET", None),
        ("/api/ceo-dashboard", "CEO Dashboard", "GET", None),
        ("/api/market-data/SPY", "Market Data", "GET", None),
        ("/api/13f-filings", "13F Filings", "GET", None),
        ("/api/insider-trading", "Insider Trading", "GET", None)
    ]
    
    # Check each endpoint
    results = []
    for endpoint, description, method, json_data in endpoints:
        results.append(check_endpoint(endpoint, description, method, json_data))
        print("")
    
    # Summary
    success_count = results.count(True)
    total_count = len(results)
    print("===========================================")
    print(f"Summary: {success_count}/{total_count} endpoints returning real data")
    print("===========================================")
    
    # Return success only if all endpoints return real data
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 