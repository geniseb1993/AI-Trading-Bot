#!/usr/bin/env python
"""
Comprehensive Test Script for AI Trading Bot
Tests all bot components, API connections, and management functionality
"""

import os
import sys
import requests
import json
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/test_app_fixes.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("TestAppFixes")

# Constants
MAIN_API_URL = "http://localhost:5000"
DUAL_BOT_API_URL = "http://localhost:5001"

def check_api_health(api_url, name):
    """Check if an API is healthy"""
    try:
        response = requests.get(f"{api_url}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"{name} API is healthy: {data}")
            return True
        else:
            logger.error(f"{name} API returned unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error checking {name} API health: {str(e)}")
        return False

def get_bot_status():
    """Get the status of all bots"""
    try:
        response = requests.get(f"{MAIN_API_URL}/api/bot/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            logger.info("Bot statuses retrieved successfully")
            logger.info(f"Autonomous Bot: {data['autonomous_bot']['status']}")
            logger.info(f"RSI Bot: {data['rsi_bot']['status']}")
            logger.info(f"Dual Bot: {data['dual_bot']['status']}")
            return data
        else:
            logger.error(f"Error getting bot status: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error getting bot status: {str(e)}")
        return None

def manage_bot(bot_type, action):
    """Start or stop a bot"""
    try:
        response = requests.post(
            f"{MAIN_API_URL}/api/bot/{action}/{bot_type}", 
            json={},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Successfully {action}ed {bot_type} bot: {data}")
            return True
        else:
            logger.error(f"Error {action}ing {bot_type} bot: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error {action}ing {bot_type} bot: {str(e)}")
        return False

def test_dual_bot_api():
    """Test the Dual Bot API endpoints"""
    try:
        # Check health endpoint
        if not check_api_health(DUAL_BOT_API_URL, "Dual Bot"):
            return False
        
        # Test market data endpoint
        try:
            response = requests.get(f"{DUAL_BOT_API_URL}/api/market-data/AAPL", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Dual Bot market data retrieved: {data}")
            else:
                logger.warning(f"Dual Bot market data endpoint failed: {response.status_code}")
        except Exception as e:
            logger.warning(f"Error testing Dual Bot market data endpoint: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing Dual Bot API: {str(e)}")
        return False

def comprehensive_test():
    """Run a comprehensive test of all bot components"""
    results = {
        "main_api_health": False,
        "dual_bot_api_health": False,
        "bot_status_retrieval": False,
        "autonomous_bot_start": False,
        "autonomous_bot_stop": False,
        "rsi_bot_start": False,
        "rsi_bot_stop": False,
        "dual_bot_start": False,
        "dual_bot_stop": False
    }
    
    # Test 1: Check if the main API is running
    logger.info("Testing Main API health...")
    results["main_api_health"] = check_api_health(MAIN_API_URL, "Main")
    
    # Test 2: Check if the Dual Bot API is running
    logger.info("Testing Dual Bot API health...")
    results["dual_bot_api_health"] = test_dual_bot_api()
    
    # Test 3: Check if we can get the status of all bots
    logger.info("Testing bot status retrieval...")
    bot_status = get_bot_status()
    results["bot_status_retrieval"] = bot_status is not None
    
    if bot_status:
        # Test 4-9: Test starting and stopping each bot
        bot_types = ["autonomous", "rsi", "dual"]
        
        for bot_type in bot_types:
            # Start the bot if it's not already running
            current_status = bot_status.get(f"{bot_type}_bot", {}).get("status", False)
            
            if not current_status:
                logger.info(f"Testing {bot_type} bot start...")
                results[f"{bot_type}_bot_start"] = manage_bot(bot_type, "start")
                time.sleep(2)  # Give it time to start
            else:
                logger.info(f"{bot_type} bot is already running, skipping start test")
                results[f"{bot_type}_bot_start"] = True
            
            # Stop the bot (whether we started it or it was already running)
            logger.info(f"Testing {bot_type} bot stop...")
            results[f"{bot_type}_bot_stop"] = manage_bot(bot_type, "stop")
            time.sleep(2)  # Give it time to stop
            
            # Start it again so we leave it in a running state
            logger.info(f"Restarting {bot_type} bot...")
            manage_bot(bot_type, "start")
            time.sleep(1)
    
    # Calculate overall success
    success_count = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    logger.info("=" * 50)
    logger.info(f"Test Results: {success_count}/{total_tests} tests passed")
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info("=" * 50)
    
    return all(results.values())

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    logger.info("Starting comprehensive bot tests...")
    success = comprehensive_test()
    
    if success:
        logger.info("All tests passed! The system appears to be working correctly.")
        sys.exit(0)
    else:
        logger.warning("Some tests failed. See the log for details.")
        sys.exit(1) 