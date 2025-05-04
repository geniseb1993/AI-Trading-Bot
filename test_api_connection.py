import requests
import sys
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("api_test")

def test_health_endpoint(base_url="http://localhost:5001"):
    """Test the API health endpoint."""
    url = f"{base_url}/api/health"
    logger.info(f"Testing health endpoint: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Response data: {data}")
            
            if data.get('status') == 'healthy':
                logger.info("Health check passed!")
                return True
            else:
                logger.error(f"Unexpected response data: {data}")
        else:
            logger.error(f"Unexpected status code: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Error connecting to API: {str(e)}")
    
    return False

def test_status_endpoint(base_url="http://localhost:5001"):
    """Test the API status endpoint."""
    url = f"{base_url}/api/status"
    logger.info(f"Testing status endpoint: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Response data: {data}")
            logger.info("Status check passed!")
            return True
        else:
            logger.error(f"Unexpected status code: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Error connecting to API: {str(e)}")
    
    return False

def main():
    """Main function to test API connection."""
    logger.info("Starting API connection test...")
    
    # Give server some time to start if needed
    logger.info("Waiting 5 seconds to ensure server is running...")
    time.sleep(5)
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    
    # Test status endpoint
    status_ok = test_status_endpoint()
    
    # Print summary
    logger.info("=== Test Summary ===")
    logger.info(f"Health Endpoint: {'OK' if health_ok else 'FAILED'}")
    logger.info(f"Status Endpoint: {'OK' if status_ok else 'FAILED'}")
    
    if health_ok and status_ok:
        logger.info("API server is running correctly!")
        return 0
    else:
        logger.error("API server has issues!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 