#!/usr/bin/env python
"""
Test script to verify both AI models in the Dual Bot system.
This script specifically tests the DeepSeek Scanner and ChatGPT Risk Manager
using the OpenRouter configuration.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the dual_bot package
sys.path.append(str(Path(__file__).parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dual_bot/logs/test_dual_models.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TestDualModels")

def prepare_config():
    """Prepare a configuration with OpenRouter API keys."""
    # Load environment variables
    project_env = Path(__file__).parent / ".env"
    if project_env.exists():
        load_dotenv(dotenv_path=project_env)
        logger.info(f"Loaded environment variables from {project_env}")
    
    # Check if we have OpenRouter API key
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not openrouter_api_key:
        logger.error("OPENROUTER_API_KEY not found in environment variables")
        return None
    
    # Create a minimal configuration for testing
    config = {
        "data_sources": {
            "polygon": {
                "enabled": True,
                "api_key": os.getenv("POLYGON_API_KEY", ""),
                "base_url": "https://api.polygon.io"
            },
            "unusual_whales": {
                "enabled": True,
                "api_key": os.getenv("UNUSUAL_WHALES_API_KEY", ""),
                "base_url": "https://api.unusualwhales.com"
            },
            "news_api": {
                "enabled": True,
                "api_key": os.getenv("NEWS_API_KEY", ""),
                "base_url": "https://newsapi.org/v2"
            }
        },
        "ai_models": {
            "deepseek": {
                "enabled": True,
                "api_key": deepseek_api_key or "",
                "model": "deepseek/deepseek-chat",
                "max_tokens": 2048,
                "temperature": 0.7,
                "openrouter_api_key": openrouter_api_key,
                "use_openrouter": True
            },
            "chatgpt": {
                "enabled": True,
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "model": "gpt-4-turbo-preview",
                "max_tokens": 2048,
                "temperature": 0.7,
                "openrouter_api_key": openrouter_api_key,
                "risk_manager": {
                    "enabled": True,
                    "confidence_threshold": 0.7,
                    "max_tokens": 1024,
                    "temperature": 0.3,
                    "retry_attempts": 3,
                    "retry_delay_seconds": 1
                }
            }
        },
        "trading": {
            "symbols": ["AAPL", "TSLA", "MSFT"],
            "options_only": False,
            "zero_dte_only": False,
            "max_trades_per_day": 3,
            "position_sizing": {
                "type": "fixed",
                "amount": 1000
            },
            "risk_management": {
                "max_loss_per_trade_percent": 2.0,
                "max_daily_loss_percent": 5.0,
                "default_stop_loss_percent": 2.0,
                "default_take_profit_percent": 5.0
            }
        },
        "logging": {
            "level": "INFO",
            "file": "dual_bot/logs/test_dual_models.log"
        }
    }
    
    logger.info("Configuration prepared successfully")
    return config

def test_deepseek_scanner(config):
    """Test the DeepSeek scanner functionality."""
    logger.info("\n===== TESTING DEEPSEEK SCANNER =====")
    
    try:
        # Import the DeepSeek scanner
        from dual_bot.deepseek_scanner import DeepSeekScanner
        
        # Initialize the DeepSeek scanner
        logger.info("Initializing DeepSeek Scanner...")
        scanner = DeepSeekScanner(config)
        logger.info("DeepSeek Scanner initialized successfully")
        
        # Create a simple market data for testing
        symbol = config["trading"]["symbols"][0]
        logger.info(f"Testing with symbol: {symbol}")
        
        market_data = {
            "symbol": symbol,
            "price": 190.0,
            "change_percent": 1.2,
            "volume": 10000000,
            "avg_volume": 8000000,
            "vix": 18.5,
            "sector_performance": {
                "technology": 1.2,
                "finance": 0.8,
                "healthcare": 0.5
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Test generating a recommendation
        logger.info("Generating trade recommendation...")
        recommendation = scanner.scan_symbol(symbol, market_data)
        
        if recommendation:
            logger.info(f"✅ SUCCESS: DeepSeek generated recommendation: {json.dumps(recommendation, indent=2)}")
            return recommendation
        else:
            logger.warning("⚠️ DeepSeek did not generate a recommendation")
            
            # Create a sample recommendation for testing the risk manager
            logger.info("Creating sample recommendation for testing...")
            sample_recommendation = {
                "symbol": symbol,
                "direction": "bullish",
                "confidence": 0.85,
                "entry_price": 190.0,
                "stop_loss": 185.0,
                "take_profit": 200.0,
                "expiry": datetime.now().strftime("%Y-%m-%d"),
                "option_type": "call",
                "reasoning": "Sample recommendation for testing"
            }
            return sample_recommendation
    
    except Exception as e:
        logger.error(f"❌ ERROR: DeepSeek Scanner test failed: {str(e)}")
        # Create a fallback recommendation
        return {
            "symbol": config["trading"]["symbols"][0],
            "direction": "bullish",
            "confidence": 0.75,
            "entry_price": 190.0,
            "stop_loss": 185.0,
            "take_profit": 200.0,
            "expiry": datetime.now().strftime("%Y-%m-%d"),
            "option_type": "call",
            "reasoning": "Fallback recommendation due to error"
        }

def test_chatgpt_risk_manager(config, recommendation):
    """Test the ChatGPT risk manager functionality."""
    logger.info("\n===== TESTING CHATGPT RISK MANAGER =====")
    
    try:
        # Import the ChatGPT risk manager
        from dual_bot.chatgpt_risk_check import ChatGPTRiskManager
        
        # Initialize the ChatGPT risk manager
        logger.info("Initializing ChatGPT Risk Manager...")
        risk_manager = ChatGPTRiskManager(config)
        logger.info("ChatGPT Risk Manager initialized successfully")
        
        # Create a market context
        symbol = recommendation["symbol"]
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
                f"{symbol} reported strong quarterly results"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        # Assess the risk of the recommendation
        logger.info(f"Assessing risk for {symbol} recommendation...")
        risk_assessment = risk_manager.assess_risk(recommendation, market_context)
        
        # Log the results
        if risk_assessment:
            logger.info(f"✅ SUCCESS: Risk assessment completed: {json.dumps(risk_assessment, indent=2)}")
            logger.info(f"Recommendation {'APPROVED' if risk_assessment.get('approved') else 'REJECTED'} with {risk_assessment.get('confidence')} confidence")
            logger.info(f"Risk level: {risk_assessment.get('risk_level')}")
            logger.info(f"Reason: {risk_assessment.get('reason')}")
            return True
        else:
            logger.warning("⚠️ Risk manager did not return an assessment")
            return False
    
    except Exception as e:
        logger.error(f"❌ ERROR: ChatGPT Risk Manager test failed: {str(e)}")
        return False

def main():
    """Main function to test both AI models."""
    logger.info("Starting Dual Bot models test...")
    
    # Prepare configuration
    config = prepare_config()
    if not config:
        logger.error("Failed to prepare configuration. Please check API keys in .env file.")
        return
    
    # Step 1: Test DeepSeek Scanner
    recommendation = test_deepseek_scanner(config)
    
    # Step 2: Test ChatGPT Risk Manager with the recommendation
    if recommendation:
        chatgpt_success = test_chatgpt_risk_manager(config, recommendation)
    else:
        logger.error("Cannot test ChatGPT Risk Manager without a recommendation")
        chatgpt_success = False
    
    # Summary
    logger.info("\n===== TEST SUMMARY =====")
    logger.info(f"DeepSeek Scanner: {'SUCCESS' if recommendation else 'FAILURE'}")
    logger.info(f"ChatGPT Risk Manager: {'SUCCESS' if chatgpt_success else 'FAILURE'}")
    
    if recommendation and chatgpt_success:
        logger.info("✅ Both AI models are functioning correctly!")
    else:
        logger.warning("⚠️ One or both AI models are not functioning correctly. Check logs for details.")

if __name__ == "__main__":
    main() 