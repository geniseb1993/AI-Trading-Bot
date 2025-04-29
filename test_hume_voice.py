"""
Test script for voice and desktop notifications using Hume AI

This script tests both desktop notifications and voice notifications
to ensure they're properly configured and working.
"""

import logging
import os
import time
import requests
import json
import platform
import sys

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Define API endpoints based on platform
BASE_URL = "http://localhost:5000"
if platform.system() == "Windows":
    # Windows sometimes uses a different port
    BASE_URL = "http://127.0.0.1:5000"

DESKTOP_NOTIFICATION_URL = f"{BASE_URL}/api/notifications/desktop"
VOICE_NOTIFICATION_URL = f"{BASE_URL}/api/notifications/speak"

def print_header(message):
    """Print a header message with decoration"""
    border = "=" * (len(message) + 4)
    print(f"\n{border}\n= {message} =\n{border}\n")

def test_desktop_notification():
    """Test sending a desktop notification"""
    print_header("Testing Desktop Notification")
    
    try:
        logger.info("Sending desktop notification test request")
        response = requests.post(
            DESKTOP_NOTIFICATION_URL,
            json={
                "title": "Test Desktop Notification",
                "message": "This is a test desktop notification from the AI Trading Bot",
                "priority": "medium"
            },
            timeout=10
        )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Desktop notification response: {result}")
            if result.get('success'):
                print("✅ Desktop notification sent successfully")
                return True
            else:
                print(f"❌ Failed to send desktop notification: {result.get('message')}")
                return False
        else:
            logger.error(f"HTTP error: {response.status_code}")
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending desktop notification: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return False

def test_voice_notification():
    """Test sending a voice notification using Hume AI"""
    print_header("Testing Voice Notification (Hume AI)")
    
    try:
        logger.info("Sending voice notification test request")
        response = requests.post(
            VOICE_NOTIFICATION_URL,
            json={
                "message": "This is a test voice notification from the AI Trading Bot. A trading opportunity has been detected for Apple at $195.67.",
                "priority": "medium",
                "use_hume": True
            },
            timeout=30  # Voice synthesis might take longer
        )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Voice notification response: {result}")
            if result.get('success'):
                print("✅ Voice notification sent successfully")
                return True
            else:
                print(f"❌ Failed to send voice notification: {result.get('message')}")
                logger.error(f"API error details: {result.get('details', 'No details provided')}")
                return False
        else:
            logger.error(f"HTTP error: {response.status_code}")
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending voice notification: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return False

def run_all_tests():
    """Run all notification tests"""
    print_header("NOTIFICATION SYSTEM TESTS")
    
    desktop_result = test_desktop_notification()
    # Short pause between tests
    time.sleep(2)
    voice_result = test_voice_notification()
    
    # Print summary
    print_header("TEST RESULTS")
    print(f"Desktop Notification: {'✅ PASSED' if desktop_result else '❌ FAILED'}")
    print(f"Voice Notification:   {'✅ PASSED' if voice_result else '❌ FAILED'}")
    
    # Final result
    if desktop_result and voice_result:
        print("\n✅ All tests passed! The notification system is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the logs for details.")
        return False

if __name__ == "__main__":
    run_all_tests() 