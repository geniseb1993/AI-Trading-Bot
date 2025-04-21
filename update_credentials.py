#!/usr/bin/env python
"""
Update API credentials in the bot management files
"""
import os
import re
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_credentials():
    """Update API credentials in files"""
    # Load environment variables
    load_dotenv()
    
    # Get API keys
    alpaca_api_key = os.getenv('ALPACA_API_KEY')
    alpaca_secret_key = os.getenv('ALPACA_API_SECRET')
    polygon_api_key = os.getenv('POLYGON_API_KEY')
    
    if not all([alpaca_api_key, alpaca_secret_key, polygon_api_key]):
        logger.error("Missing required API keys in .env file")
        return False
    
    try:
        # Update DualBotManager
        dual_bot_file = 'api/dual_bot/dual_bot_manager.py'
        if os.path.exists(dual_bot_file):
            with open(dual_bot_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace hardcoded values with config references
            content = re.sub(
                r'self\.polygon_client = RESTClient\(api_key="[^"]*"\)',
                'self.polygon_client = RESTClient(api_key=bot_config.POLYGON_API_KEY)',
                content
            )
            content = re.sub(
                r'self\.alpaca_client = TradingClient\("[^"]*", "[^"]*"\)',
                'self.alpaca_client = TradingClient(bot_config.ALPACA_API_KEY, bot_config.ALPACA_SECRET_KEY, paper=bot_config.PAPER_TRADING)',
                content
            )
            
            with open(dual_bot_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Updated credentials in {dual_bot_file}")
        
        # Create necessary directories
        os.makedirs('api/dual_bot', exist_ok=True)
        os.makedirs('api/execution_model', exist_ok=True)
        os.makedirs('api/broker_integration', exist_ok=True)
        os.makedirs('api/config', exist_ok=True)
        os.makedirs('api/routes', exist_ok=True)
        
        logger.info("Successfully updated credentials in all files")
        return True
    
    except Exception as e:
        logger.error(f"Error updating credentials: {str(e)}")
        return False

if __name__ == "__main__":
    success = update_credentials()
    if success:
        print("Credentials updated successfully")
    else:
        print("Failed to update credentials") 