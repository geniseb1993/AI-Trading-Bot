#!/usr/bin/env python3
"""
Test script to verify that all API routes in the Flask application are working properly.
This script will make requests to all endpoints and check for correct responses.
"""

import requests
import json
import sys
from datetime import datetime
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

# Base URL for the API
BASE_URL = "http://localhost:5000"

def print_status(message, status):
    """Print a formatted status message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if status == "pass":
        print(f"{Fore.GREEN}[{timestamp}] ✓ PASS: {message}{Style.RESET_ALL}")
    elif status == "fail":
        print(f"{Fore.RED}[{timestamp}] ✗ FAIL: {message}{Style.RESET_ALL}")
    elif status == "warn":
        print(f"{Fore.YELLOW}[{timestamp}] ⚠ WARN: {message}{Style.RESET_ALL}")
    elif status == "info":
        print(f"{Fore.BLUE}[{timestamp}] ℹ INFO: {message}{Style.RESET_ALL}")
    else:
        print(f"[{timestamp}] {message}")

def test_endpoint(endpoint, method="GET", data=None, expected_status=200, expected_fields=None):
    """Test an API endpoint and check the response"""
    url = f"{BASE_URL}{endpoint}"
    print_status(f"Testing {method} {endpoint}", "info")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            print_status(f"Unsupported method: {method}", "fail")
            return False
        
        # Check status code
        if response.status_code != expected_status:
            print_status(f"Expected status {expected_status}, got {response.status_code}: {response.text}", "fail")
            return False
        
        # Parse response
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            print_status(f"Failed to parse JSON response: {response.text}", "fail")
            return False
        
        # Check expected fields if specified
        if expected_fields:
            missing_fields = []
            for field in expected_fields:
                if field not in response_data:
                    missing_fields.append(field)
            
            if missing_fields:
                print_status(f"Missing expected fields: {missing_fields}", "fail")
                return False
        
        print_status(f"Endpoint {endpoint} responded correctly with {len(str(response_data))} bytes", "pass")
        return True
    
    except Exception as e:
        print_status(f"Error testing {endpoint}: {str(e)}", "fail")
        return False

def run_all_tests():
    """Run all API endpoint tests"""
    print_status("Starting API endpoint tests", "info")
    
    # Track test results
    test_results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    # Test basic health endpoints
    test_results["total"] += 1
    if test_endpoint("/api/test", expected_fields=["success", "message"]):
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    test_results["total"] += 1
    if test_endpoint("/api/health", expected_fields=["status"]):
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    # Test institutional flow endpoints
    test_results["total"] += 1
    if test_endpoint("/api/institutional-flow", expected_fields=["success", "data"]):
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    test_results["total"] += 1
    filter_data = {
        "symbols": ["AAPL", "MSFT"],
        "flowType": "darkpool"
    }
    if test_endpoint("/api/institutional-flow/get-data", method="POST", data=filter_data, expected_fields=["success", "data"]):
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    # Test market analysis endpoints
    test_results["total"] += 1
    analysis_data = {
        "timeframe": "1d"
    }
    if test_endpoint("/api/market-analysis/get-data", method="POST", data=analysis_data, expected_fields=["success"]):
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    test_results["total"] += 1
    insights_data = {
        "timeframe": "1d"
    }
    if test_endpoint("/api/ai-insights/market-analysis", method="POST", data=insights_data, expected_fields=["success"]):
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    # Test market data endpoint
    test_results["total"] += 1
    if test_endpoint("/api/market-data/AAPL?timeframe=1d&days=30", expected_fields=["success", "symbol"]):
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    # Print summary
    print("\n" + "="*50)
    print_status(f"Test Summary: {test_results['passed']}/{test_results['total']} tests passed", "info")
    
    if test_results["failed"] > 0:
        print_status(f"{test_results['failed']} tests failed", "warn")
        return False
    else:
        print_status("All tests passed!", "pass")
        return True

if __name__ == "__main__":
    print("\n" + "="*50)
    print(f" API Route Testing Tool - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50 + "\n")
    
    success = run_all_tests()
    
    if not success:
        sys.exit(1)
    sys.exit(0) 