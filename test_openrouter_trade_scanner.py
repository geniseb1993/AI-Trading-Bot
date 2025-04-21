#!/usr/bin/env python
"""
OpenRouter Trade Scanner Test Script
This script tests if the DeepSeek models work correctly with OpenRouter to generate trade recommendations.
"""

import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TradeScannerTest")

def test_trade_scanner():
    """Test the DeepSeek model's ability to generate trade recommendations."""
    logger.info("Starting Trade Scanner test with OpenRouter (DeepSeek model)...")
    
    # Load environment variables
    load_dotenv()
    
    # Get OpenRouter API key
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        logger.error("OPENROUTER_API_KEY not found in environment variables")
        return False
    
    logger.info(f"OpenRouter API key: {openrouter_api_key[:10]}...")
    
    # Create a sample market data
    symbol = "TSLA"
    market_data = {
        "symbol": symbol,
        "price": 215.75,
        "change_percent": 2.3,
        "volume": 25000000,
        "avg_volume": 20000000,
        "sma_50": 205.30,
        "sma_200": 198.75,
        "rsi": 68.2,
        "macd": 3.5,
        "macd_signal": 2.1
    }
    
    try:
        # Initialize the OpenAI client with OpenRouter configuration
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key
        )
        
        # Format the prompt for trade recommendation - more structured and explicit
        prompt = f"""
You are a stock market analyst. You need to analyze market data for {symbol} and generate a trading recommendation.

Here is the market data:
- Current price: ${market_data['price']}
- Percent change: {market_data['change_percent']}%
- Volume: {market_data['volume']}
- Average volume: {market_data['avg_volume']}
- 50-day SMA: ${market_data['sma_50']}
- 200-day SMA: ${market_data['sma_200']}
- RSI: {market_data['rsi']}
- MACD: {market_data['macd']}
- MACD Signal: {market_data['macd_signal']}

Respond ONLY with a JSON object in this exact format:
{{
    "symbol": "{symbol}",
    "direction": "bullish",
    "confidence": 0.85,
    "entry_price": 215.75,
    "stop_loss": 210.00,
    "take_profit": 225.00,
    "reasoning": "Detailed explanation"
}}

Where:
- "direction" must be either "bullish", "bearish", or "neutral"
- "confidence" must be a number between 0 and 1
- "entry_price", "stop_loss", and "take_profit" must be numeric values
- "reasoning" must explain your analysis

Your response must contain valid JSON only, with no additional text before or after.
"""
        
        logger.info(f"Sending trade scanner request to OpenRouter (DeepSeek model) for {symbol}...")
        
        # Make the API call
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1",  # Try a different model
            messages=[
                {"role": "system", "content": "You are an expert financial analyst. Your task is to analyze stock data and generate valid JSON trade recommendations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.3,  # Reduced temperature for more deterministic output
            extra_headers={
                "HTTP-Referer": "https://ai-trading-bot.com",
                "X-Title": "AI Trading Bot"
            }
        )
        
        # Get the response text
        response_text = response.choices[0].message.content
        logger.info(f"Response received from OpenRouter (DeepSeek):\n{response_text}")
        
        # Parse the JSON from the response
        try:
            # Clean the response text to extract just the JSON
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            recommendation = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['symbol', 'direction', 'confidence', 'entry_price', 'stop_loss', 'take_profit', 'reasoning']
            for field in required_fields:
                if field not in recommendation:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Log the recommendation
            logger.info("Trade recommendation parsed successfully:")
            logger.info(f"Symbol: {recommendation['symbol']}")
            logger.info(f"Direction: {recommendation['direction']}")
            logger.info(f"Confidence: {recommendation['confidence']}")
            logger.info(f"Entry Price: {recommendation['entry_price']}")
            logger.info(f"Stop Loss: {recommendation['stop_loss']}")
            logger.info(f"Take Profit: {recommendation['take_profit']}")
            logger.info(f"Reasoning: {recommendation['reasoning']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error parsing trade recommendation: {str(e)}")
            logger.error(f"Raw response: {response_text}")
            return False
        
    except Exception as e:
        logger.error(f"Error in trade scanner: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_trade_scanner()
    if success:
        logger.info("Trade Scanner test with OpenRouter completed successfully!")
    else:
        logger.error("Trade Scanner test with OpenRouter failed!")
        sys.exit(1) 