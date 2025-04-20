"""
Test script for CEO Dashboard API endpoints
"""
import requests
import json
import time
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base URL for the API
BASE_URL = "http://localhost:5000/api"

def test_ceo_dashboard():
    """Test the CEO dashboard endpoint"""
    logger.info("Testing CEO dashboard endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/ceo-dashboard")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Dashboard endpoint returned successfully with status code: {response.status_code}")
            logger.info(f"Response contains: {list(data.keys())}")
            return True
        else:
            logger.error(f"Dashboard endpoint failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error testing dashboard endpoint: {str(e)}")
        return False

def test_ceo_settings():
    """Test the CEO settings endpoint"""
    logger.info("Testing CEO settings endpoint...")
    
    try:
        # Test GET request
        get_response = requests.get(f"{BASE_URL}/ceo-settings")
        if get_response.status_code == 200:
            data = get_response.json()
            logger.info(f"Settings GET endpoint returned successfully with status code: {get_response.status_code}")
            logger.info(f"Response contains: {list(data.keys())}")
            
            # Test POST request - update a setting
            settings = data.get('settings', {})
            if settings:
                original_auto_trading = settings.get('autoTrading', False)
                settings['autoTrading'] = not original_auto_trading
                
                post_response = requests.post(
                    f"{BASE_URL}/ceo-settings", 
                    json=settings
                )
                
                if post_response.status_code == 200:
                    updated_data = post_response.json()
                    logger.info(f"Settings POST endpoint returned successfully with status code: {post_response.status_code}")
                    updated_auto_trading = updated_data.get('settings', {}).get('autoTrading')
                    
                    if updated_auto_trading == (not original_auto_trading):
                        logger.info("Settings were successfully updated")
                    else:
                        logger.warning("Settings may not have been updated correctly")
                else:
                    logger.error(f"Settings POST endpoint failed with status code: {post_response.status_code}")
                    logger.error(f"Response: {post_response.text}")
            
            return True
        else:
            logger.error(f"Settings endpoint failed with status code: {get_response.status_code}")
            logger.error(f"Response: {get_response.text}")
            return False
    except Exception as e:
        logger.error(f"Error testing settings endpoint: {str(e)}")
        return False

def test_trade_setup_endpoints():
    """Test the trade setup approval and rejection endpoints"""
    logger.info("Testing trade setup endpoints...")
    
    setup_id = f"test_setup_{int(time.time())}"
    
    try:
        # Test approve endpoint
        approve_response = requests.post(
            f"{BASE_URL}/approve-trade-setup",
            json={"setupId": setup_id}
        )
        
        if approve_response.status_code == 200:
            data = approve_response.json()
            logger.info(f"Approve trade setup endpoint returned successfully with status code: {approve_response.status_code}")
            logger.info(f"Response: {data}")
            
            # Test reject endpoint with a new setup ID
            reject_id = f"{setup_id}_reject"
            reject_response = requests.post(
                f"{BASE_URL}/reject-trade-setup",
                json={"setupId": reject_id}
            )
            
            if reject_response.status_code == 200:
                reject_data = reject_response.json()
                logger.info(f"Reject trade setup endpoint returned successfully with status code: {reject_response.status_code}")
                logger.info(f"Response: {reject_data}")
                return True
            else:
                logger.error(f"Reject trade setup endpoint failed with status code: {reject_response.status_code}")
                logger.error(f"Response: {reject_response.text}")
                return False
        else:
            logger.error(f"Approve trade setup endpoint failed with status code: {approve_response.status_code}")
            logger.error(f"Response: {approve_response.text}")
            return False
    except Exception as e:
        logger.error(f"Error testing trade setup endpoints: {str(e)}")
        return False

def run_all_tests():
    """Run all CEO dashboard API tests"""
    logger.info("Starting CEO dashboard API tests...")
    
    # Retry mechanism for testing connectivity
    max_retries = 5
    retry_delay = 2  # seconds
    
    for i in range(max_retries):
        try:
            # Try a simple GET request to see if the server is up
            requests.get(f"{BASE_URL}/test", timeout=2)
            logger.info("API server is accessible")
            break
        except requests.exceptions.ConnectionError:
            if i < max_retries - 1:
                logger.warning(f"API server not accessible, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("API server is not accessible after multiple attempts")
                return False
    
    # Run all tests
    dashboard_result = test_ceo_dashboard()
    settings_result = test_ceo_settings()
    trade_setup_result = test_trade_setup_endpoints()
    
    # Summarize results
    results = {
        "Dashboard": "PASS" if dashboard_result else "FAIL",
        "Settings": "PASS" if settings_result else "FAIL",
        "Trade Setup": "PASS" if trade_setup_result else "FAIL"
    }
    
    logger.info("CEO Dashboard API Tests Results:")
    for test_name, result in results.items():
        logger.info(f"  {test_name}: {result}")
    
    overall_result = all([dashboard_result, settings_result, trade_setup_result])
    logger.info(f"Overall test result: {'PASS' if overall_result else 'FAIL'}")
    
    return overall_result

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 