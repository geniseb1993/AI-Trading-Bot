"""
Health check endpoint for the API
"""

from flask import Blueprint, jsonify
import os
import logging
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__, url_prefix='/api')

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify API is running and check Alpaca connectivity
    """
    alpaca_connected = False
    
    # Check Alpaca API connection
    try:
        alpaca_key = os.environ.get('ALPACA_API_KEY')
        alpaca_secret = os.environ.get('ALPACA_API_SECRET')
        alpaca_url = os.environ.get('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        # Only attempt to check connection if credentials are available
        if alpaca_key and alpaca_secret:
            # Try to make a simple request to the Alpaca API
            headers = {
                'APCA-API-KEY-ID': alpaca_key,
                'APCA-API-SECRET-KEY': alpaca_secret
            }
            account_url = f"{alpaca_url}/v2/account"
            response = requests.get(account_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                alpaca_connected = True
                logger.info("Alpaca API connection successful")
            else:
                logger.warning(f"Alpaca API connection failed with status code: {response.status_code}")
        else:
            logger.warning("Alpaca API credentials not found in environment variables")
    except Exception as e:
        logger.error(f"Error checking Alpaca connection: {str(e)}")
    
    return jsonify({
        'status': 'ok',
        'message': 'API is running',
        'alpaca_connected': alpaca_connected
    }) 