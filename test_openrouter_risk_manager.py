#!/usr/bin/env python
"""
OpenRouter Risk Manager Test Script
This script tests if the ChatGPT Risk Manager works correctly with OpenRouter.
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
logger = logging.getLogger("RiskManagerTest")

def test_risk_manager():
    """Test the risk manager's ability to assess a trade."""
    logger.info("Starting Risk Manager test with OpenRouter...")
    
    # Load environment variables
    load_dotenv()
    
    # Get OpenRouter API key
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        logger.error("OPENROUTER_API_KEY not found in environment variables")
        return False
    
    logger.info(f"OpenRouter API key: {openrouter_api_key[:10]}...")
    
    # Create a sample trade recommendation
    trade_recommendation = {
        "symbol": "AAPL",
        "direction": "bullish",
        "confidence": 0.85,
        "entry_price": 190.0,
        "stop_loss": 185.0,
        "take_profit": 200.0,
        "expiry": datetime.now().strftime("%Y-%m-%d"),
        "option_type": "call",
        "reasoning": "Strong momentum and positive market sentiment"
    }
    
    # Create a sample market context
    market_context = {
        "market_hours": "open",
        "market_condition": "bullish",
        "vix": 18.5,
        "sector_performance": {
            "technology": 1.2,
            "finance": 0.8,
            "healthcare": 0.5
        },
        "recent_news": [
            "Fed signals potential rate cut",
            "Tech sector leads market gains",
            "AAPL reported strong quarterly results"
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # Initialize the OpenAI client with OpenRouter configuration
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key
        )
        
        # Format the prompt for risk assessment
        prompt = f"""
Please analyze the following trade recommendation and provide a risk assessment:

Trade Recommendation:
{json.dumps(trade_recommendation, indent=2)}

Market Context:
{json.dumps(market_context, indent=2)}

Provide a risk assessment in the following JSON format:
{{
    "approved": boolean,
    "confidence": float (0-1),
    "risk_level": "LOW" | "MEDIUM" | "HIGH",
    "reason": "Detailed explanation of the risk assessment"
}}

Consider the following factors:
1. Market conditions and volatility
2. Technical indicators and signals
3. News sentiment and impact
4. Position sizing and risk management
"""
        
        logger.info("Sending risk assessment request to OpenRouter...")
        
        # Make the API call
        response = client.chat.completions.create(
            model="openai/gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a professional risk analyst for a trading system. Analyze the trade recommendation and provide a structured risk assessment."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.3,
            extra_headers={
                "HTTP-Referer": "https://ai-trading-bot.com",
                "X-Title": "AI Trading Bot"
            }
        )
        
        # Get the response text
        response_text = response.choices[0].message.content
        logger.info(f"Response received from OpenRouter:\n{response_text}")
        
        # Parse the JSON from the response
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx == -1 or end_idx == 0:
                logger.error("No JSON found in response")
                return False
                
            json_str = response_text[start_idx:end_idx]
            risk_assessment = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['approved', 'confidence', 'risk_level', 'reason']
            for field in required_fields:
                if field not in risk_assessment:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Log the risk assessment
            logger.info("Risk assessment parsed successfully:")
            logger.info(f"Approved: {risk_assessment['approved']}")
            logger.info(f"Confidence: {risk_assessment['confidence']}")
            logger.info(f"Risk Level: {risk_assessment['risk_level']}")
            logger.info(f"Reason: {risk_assessment['reason']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error parsing risk assessment: {str(e)}")
            return False
        
    except Exception as e:
        logger.error(f"Error in risk assessment: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_risk_manager()
    if success:
        logger.info("Risk Manager test with OpenRouter completed successfully!")
    else:
        logger.error("Risk Manager test with OpenRouter failed!")
        sys.exit(1) 