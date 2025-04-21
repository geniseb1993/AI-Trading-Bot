import os
import sys
import json
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Force a valid model ID for testing
os.environ['DEEPSEEK_MODEL'] = 'deepseek/deepseek-r1'
print(f"Using model: deepseek/deepseek-r1")

# Import our DeepSeek client
from dual_bot.ai.deepseek_client import DeepSeekClient

def test_deepseek_client():
    """Test the DeepSeek client functionality"""
    print("\n=== Testing DeepSeek Client ===")
    
    # Create a mock config
    config = {
        "deepseek": {
            "model": "deepseek/deepseek-r1",  # Force a known valid model ID
            "max_tokens": 500,
            "temperature": 0.7
        }
    }
    
    print(f"Using model configuration: {config['deepseek']['model']}")
    
    try:
        # Initialize the client
        client = DeepSeekClient(config)
        print(f"DeepSeek client initialized successfully with model: {client.model}")
        
        # Test simple text generation
        print("\nTesting text generation...")
        response = client.generate(
            prompt="Explain how the RSI indicator can be used to identify trading opportunities.",
            system_prompt="You are an expert in technical analysis and trading."
        )
        
        print("\nResponse from DeepSeek:")
        print(response[:500] + "..." if len(response) > 500 else response)
        
        # Test market analysis functionality
        print("\nTesting market analysis...")
        market_data = {
            "symbol": "TSLA",
            "price": 196.45,
            "volume": 34562198,
            "previous_close": 193.76,
            "change_percent": 1.39,
            "market_cap": "625.8B"
        }
        
        technical_indicators = {
            "rsi": 58.2,
            "macd": -0.43,
            "ema_50": 198.32,
            "ema_200": 180.65,
            "bollinger_bands": {
                "upper": 210.45,
                "middle": 195.78,
                "lower": 181.11
            },
            "stochastic": {
                "%K": 65.34,
                "%D": 60.12
            }
        }
        
        analysis = client.analyze_market(market_data, technical_indicators)
        
        print("\nMarket Analysis Results:")
        print(json.dumps(analysis, indent=2))
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing DeepSeek client: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_deepseek_client()
    sys.exit(0 if success else 1) 