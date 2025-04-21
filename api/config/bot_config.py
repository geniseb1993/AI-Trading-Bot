import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys and Secrets
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', 'demo-key')
ALPACA_SECRET_KEY = os.getenv('ALPACA_API_SECRET', 'demo-secret')  # Using correct env var name from .env
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY', 'demo-polygon-key')
UNUSUAL_WHALES_API_KEY = os.getenv('UNUSUAL_WHALES_API_KEY', 'demo-whales-key')

# Trading Configuration
PAPER_TRADING = os.getenv('PAPER_TRADING', 'true').lower() == 'true'
MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', '10'))
RISK_PERCENTAGE = float(os.getenv('RISK_PERCENTAGE', '2.0'))
POSITION_SIZE_PERCENTAGE = float(os.getenv('POSITION_SIZE_PERCENTAGE', '5.0'))

# Data Sources Configuration
USE_POLYGON_DATA = os.getenv('USE_POLYGON_DATA', 'true').lower() == 'true'
USE_ALPACA_DATA = os.getenv('USE_ALPACA_DATA', 'true').lower() == 'true'
USE_UNUSUAL_WHALES = os.getenv('USE_UNUSUAL_WHALES', 'true').lower() == 'true'

# Bot-specific Configuration
AUTONOMOUS_BOT_CONFIG = {
    'min_volume': int(os.getenv('AUTO_MIN_VOLUME', '500000')),
    'min_price': float(os.getenv('AUTO_MIN_PRICE', '5.0')),
    'max_price': float(os.getenv('AUTO_MAX_PRICE', '500.0')),
    'stop_loss_percentage': float(os.getenv('AUTO_STOP_LOSS_PERCENTAGE', '2.0')),
    'take_profit_percentage': float(os.getenv('AUTO_TAKE_PROFIT_PERCENTAGE', '5.0')),
}

RSI_BOT_CONFIG = {
    'rsi_period': int(os.getenv('RSI_PERIOD', '14')),
    'oversold_threshold': float(os.getenv('RSI_OVERSOLD', '30')),
    'overbought_threshold': float(os.getenv('RSI_OVERBOUGHT', '70')),
    'confirmation_period': int(os.getenv('RSI_CONFIRMATION_PERIOD', '3')),
}

DUAL_BOT_CONFIG = {
    'correlation_threshold': float(os.getenv('DUAL_CORRELATION_THRESHOLD', '0.7')),
    'min_volume_ratio': float(os.getenv('DUAL_MIN_VOLUME_RATIO', '1.5')),
    'max_spread_percentage': float(os.getenv('DUAL_MAX_SPREAD_PERCENTAGE', '2.0')),
    'min_profit_threshold': float(os.getenv('DUAL_MIN_PROFIT_THRESHOLD', '0.5')),
}

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Error thresholds
MAX_API_RETRIES = int(os.getenv('MAX_API_RETRIES', '3'))
API_RETRY_DELAY = int(os.getenv('API_RETRY_DELAY', '5'))

# Validation
def validate_config():
    """Validate the configuration settings - using more lenient validation for development"""
    # Check for required variables but provide defaults for development
    for key in ['ALPACA_API_KEY', 'ALPACA_SECRET_KEY', 'POLYGON_API_KEY']:
        if not globals().get(key):
            globals()[key] = f"demo-{key.lower()}"
            print(f"WARNING: Using demo value for {key}")
    
    # Safety checks
    if RISK_PERCENTAGE > 5.0:
        print("WARNING: Risk percentage exceeds 5% - capping at 5%")
        globals()['RISK_PERCENTAGE'] = 5.0
    
    if POSITION_SIZE_PERCENTAGE > 20.0:
        print("WARNING: Position size percentage exceeds 20% - capping at 20%")
        globals()['POSITION_SIZE_PERCENTAGE'] = 20.0
    
    return True

# Validate configuration on import
validate_config() 