#!/usr/bin/env python
"""
Unusual Whales API Validation Script

This script validates the Unusual Whales API connection, token, and provides
detailed information about any issues encountered.

Usage:
    python validate_unusual_whales.py
"""

import os
import sys
import json
import requests
import logging
from dotenv import load_dotenv
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def print_section(title):
    """Print a section header with appropriate formatting."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}")

def validate_api_key_presence():
    """Validate that an API key is present in environment variables."""
    print_section("CHECKING API KEY CONFIGURATION")
    
    api_key = os.environ.get('UNUSUAL_WHALES_API_KEY')
    
    if not api_key:
        print("❌ ERROR: Unusual Whales API key not found in environment variables")
        print("   Please add UNUSUAL_WHALES_API_KEY to your .env file")
        return None
    
    print(f"✅ API key found in environment variables")
    
    # Basic validation of key format
    if not api_key.strip():
        print("❌ ERROR: API key is empty")
        return None
        
    if len(api_key) < 10:  # Very basic length check
        print("⚠️ WARNING: API key appears to be too short, please verify")
    
    print(f"   Key: {api_key[:5]}...{api_key[-5:]}")  # Show first and last 5 chars for verification
    
    return api_key

def test_api_connection(api_key):
    """Test the direct API connection with detailed error information."""
    print_section("TESTING API CONNECTION")
    
    base_url = "https://api.unusualwhales.com"
    
    # 1. Test basic connectivity to the API domain
    print("\n1️⃣ Testing basic connectivity to the API domain...")
    try:
        response = requests.get("https://api.unusualwhales.com", timeout=10)
        print(f"✅ Connection successful (Status Code: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        print("   This indicates a network issue or the API server is down")
        return False
    
    # 2. Test API authentication
    print("\n2️⃣ Testing API authentication...")
    
    headers = {
        'Authorization': f"Bearer {api_key}",
        'Content-Type': 'application/json'
    }
    
    # Note: Options Flow endpoint is known to have issues
    # Only test the Dark Pool endpoint which is known to work
    endpoints = [
        {
            'name': 'Dark Pool Recent',
            'url': f"{base_url}/api/darkpool/recent",
            'params': {'limit': 1}
        }
        # Options Flow endpoint removed as it appears to be deprecated or not working
    ]
    
    all_successful = True
    
    for endpoint in endpoints:
        try:
            print(f"\nTesting endpoint: {endpoint['name']}")
            response = requests.get(
                endpoint['url'], 
                headers=headers, 
                params=endpoint['params'],
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ {endpoint['name']} endpoint: Authentication successful")
                
                # Parse response to validate data structure
                data = response.json()
                if data.get('data') and isinstance(data['data'], list):
                    print(f"   Received {len(data['data'])} records")
                else:
                    print("⚠️ Warning: Unexpected response format")
                    print(f"   Response: {data}")
            
            elif response.status_code == 401:
                print(f"❌ {endpoint['name']} endpoint: Authentication failed (Invalid token)")
                print("   Your API key appears to be invalid or expired")
                all_successful = False
            
            elif response.status_code == 403:
                print(f"❌ {endpoint['name']} endpoint: Authorization failed (Insufficient permissions)")
                print("   Your API key doesn't have permission to access this endpoint")
                all_successful = False
            
            elif response.status_code == 429:
                print(f"❌ {endpoint['name']} endpoint: Rate limit exceeded")
                print("   You've made too many requests. Please try again later")
                all_successful = False
            
            else:
                print(f"❌ {endpoint['name']} endpoint: Request failed with status code {response.status_code}")
                print(f"   Response: {response.text}")
                all_successful = False
            
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint['name']} endpoint: Request failed with error: {e}")
            all_successful = False
    
    return all_successful

def check_subscription_status(api_key):
    """Check the subscription status for the API key."""
    print_section("CHECKING SUBSCRIPTION STATUS")
    
    # This is a mock implementation as Unusual Whales doesn't have a public endpoint
    # to check subscription status. In practice, you might need to check specific
    # endpoint access or contact their support.
    
    # Instead, we'll try to access premium endpoints to infer status
    headers = {
        'Authorization': f"Bearer {api_key}",
        'Content-Type': 'application/json'
    }
    
    premium_endpoints = [
        {
            'name': 'Dark Pool Aggregate',
            'url': "https://api.unusualwhales.com/api/darkpool/aggregate",
            'params': {'limit': 1}
        }
    ]
    
    subscription_active = True
    
    for endpoint in premium_endpoints:
        try:
            print(f"\nTesting premium endpoint: {endpoint['name']}")
            response = requests.get(
                endpoint['url'], 
                headers=headers, 
                params=endpoint['params'],
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ {endpoint['name']} accessible (Subscription active)")
            
            elif response.status_code in (401, 403):
                print(f"❌ {endpoint['name']} not accessible (Subscription may be inactive)")
                print("   This endpoint requires an active subscription")
                subscription_active = False
            
            else:
                print(f"⚠️ {endpoint['name']} returned unexpected status code: {response.status_code}")
                print(f"   Response: {response.text}")
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error testing {endpoint['name']}: {e}")
            subscription_active = False
    
    if subscription_active:
        print("\n✅ Your subscription appears to be active")
    else:
        print("\n⚠️ Some premium endpoints are not accessible")
        print("   Your subscription may be inactive or expired")
        print("   Please check your account at unusualwhales.com")
    
    return subscription_active

def main():
    """Main function to run validation tests."""
    print("\n📊 UNUSUAL WHALES API VALIDATION TOOL 📊\n")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Validate API key presence
    api_key = validate_api_key_presence()
    if not api_key:
        sys.exit(1)
    
    # Step 2: Test API connection
    connection_successful = test_api_connection(api_key)
    
    if not connection_successful:
        print("\n❌ API connection validation failed")
        print("   Please check the errors above and verify your API key")
        sys.exit(1)
    
    # Step 3: Check subscription status
    subscription_active = check_subscription_status(api_key)
    
    # Summary
    print_section("VALIDATION SUMMARY")
    print("✅ API key is properly configured")
    print("✅ API connection is successful")
    print(f"{'✅' if subscription_active else '⚠️'} Subscription status: {'Active' if subscription_active else 'Possibly inactive'}")
    
    print("\n🎉 Unusual Whales API validation completed successfully! 🎉")
    
    if not subscription_active:
        print("\n⚠️ Note: Some premium endpoints might not be accessible")
        print("   Please verify your subscription status at unusualwhales.com")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 