#!/usr/bin/env python
"""
Test script for dashboard routes
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:5000"

def test_dashboard():
    """Test the main dashboard endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/dashboard")
        if response.status_code == 200:
            data = response.json()
            print("✓ Dashboard API success!")
            print(f"Data keys: {list(data.keys())}")
            if "dashboard" in data:
                print(f"Dashboard keys: {list(data['dashboard'].keys())}")
            return True
        else:
            print(f"✗ Dashboard API error: Status code {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"✗ Error testing dashboard: {e}")
        return False

def test_market_overview():
    """Test the market overview endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/market-overview")
        if response.status_code == 200:
            data = response.json()
            print("✓ Market Overview API success!")
            print(f"Data keys: {list(data.keys())}")
            if "market_overview" in data:
                print(f"Market overview indices: {len(data['market_overview']['indices'])}")
            return True
        else:
            print(f"✗ Market Overview API error: Status code {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"✗ Error testing market overview: {e}")
        return False

def test_portfolio_performance():
    """Test the portfolio performance endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/portfolio-performance")
        if response.status_code == 200:
            data = response.json()
            print("✓ Portfolio Performance API success!")
            print(f"Data keys: {list(data.keys())}")
            if "performance" in data:
                print(f"Performance keys: {list(data['performance'].keys())}")
            return True
        else:
            print(f"✗ Portfolio Performance API error: Status code {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"✗ Error testing portfolio performance: {e}")
        return False

def test_ceo_dashboard():
    """Test the CEO dashboard endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/ceo-dashboard")
        if response.status_code == 200:
            data = response.json()
            print("✓ CEO Dashboard API success!")
            print(f"Data keys: {list(data.keys())}")
            return True
        else:
            print(f"✗ CEO Dashboard API error: Status code {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"✗ Error testing CEO dashboard: {e}")
        return False

def main():
    """Main function"""
    print("\n=== Testing Dashboard Routes ===\n")
    
    dashboard_result = test_dashboard()
    print("\n")
    
    market_overview_result = test_market_overview()
    print("\n")
    
    portfolio_result = test_portfolio_performance()
    print("\n")
    
    ceo_result = test_ceo_dashboard()
    print("\n")
    
    # Summary
    print("=== Test Summary ===")
    print(f"Dashboard API: {'✓' if dashboard_result else '✗'}")
    print(f"Market Overview API: {'✓' if market_overview_result else '✗'}")
    print(f"Portfolio Performance API: {'✓' if portfolio_result else '✗'}")
    print(f"CEO Dashboard API: {'✓' if ceo_result else '✗'}")
    
    # Exit with proper code
    if dashboard_result and market_overview_result and portfolio_result and ceo_result:
        print("\nAll routes are working! ✓")
        return 0
    else:
        print("\nSome routes are not working properly. ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 