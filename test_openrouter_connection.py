import os
import sys
import openai
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("OPENROUTER_API_KEY")
model = os.getenv("OPENROUTER_MODEL") or "deepseek/deepseek-r1"  # Use a valid model ID

# Validate API key
if not api_key:
    print("Error: OPENROUTER_API_KEY not found in .env file")
    print("Please add your OpenRouter API key to the .env file")
    print("Get your API key from: https://openrouter.ai/keys")
    sys.exit(1)

# Check API key format (OpenRouter keys typically start with sk-or or sk-proj)
if not (api_key.startswith("sk-or") or api_key.startswith("sk-proj")):
    print("Warning: Unusual OpenRouter API key format")
    print("OpenRouter API keys typically start with 'sk-or-' or 'sk-proj-'")
    print("Get a proper OpenRouter key from: https://openrouter.ai/keys")

print(f"Testing OpenRouter connection with model: {model}")
print(f"API key format: {'Valid ✓' if api_key.startswith('sk-or') or api_key.startswith('sk-proj') else 'Warning: Unusual format'}")
print("Sending test request to OpenRouter API...")

try:
    # Initialize the OpenAI client with OpenRouter configuration
    client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "https://ai-trading-bot.com",  # Optional: your site URL
            "X-Title": "AI Trading Bot"                    # Optional: your site name
        }
    )
    
    # Test data for analysis
    market_data = {
        "symbol": "AAPL",
        "price": 185.64,
        "volume": 54892651,
        "previous_close": 183.12,
        "52wk_high": 198.23,
        "52wk_low": 145.67
    }
    
    technical_indicators = {
        "rsi": 63.5,
        "macd": 2.34,
        "ema_50": 182.45,
        "ema_200": 175.23,
        "bollinger_upper": 195.24,
        "bollinger_lower": 175.78
    }
    
    # Create a proper trading analysis prompt
    prompt = f"""
    Please analyze the following market data and technical indicators for {market_data['symbol']}.
    
    Market Data:
    {json.dumps(market_data, indent=2)}
    
    Technical Indicators:
    {json.dumps(technical_indicators, indent=2)}
    
    Provide a brief trading recommendation in JSON format:
    {{
        "recommendation": "buy" | "sell" | "hold",
        "confidence": float between 0-1,
        "reasoning": "brief explanation"
    }}
    """
    
    # Test API connection with a simple completion
    print(f"Requesting analysis from model: {model}")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert market analyst providing concise trading insights."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )
    
    # Print the response
    print("\nResponse from OpenRouter API (DeepSeek model):")
    print(f"Status: Success")
    print(f"Model used: {response.model}")
    print(f"\nTrading analysis:")
    print(f"{response.choices[0].message.content}")
    
except openai.AuthenticationError as e:
    print("\nAuthentication Error:")
    print("Your OpenRouter API key is invalid or expired.")
    print("Please get a new API key from: https://openrouter.ai/keys")
    print(f"Error details: {str(e)}")
    
except openai.RateLimitError:
    print("\nRate Limit Error:")
    print("You've exceeded your OpenRouter rate limit. Please try again later.")
    
except openai.APIConnectionError:
    print("\nConnection Error:")
    print("Could not connect to the OpenRouter API. Please check your internet connection.")
    
except Exception as e:
    print(f"\nError connecting to OpenRouter API: {str(e)}") 