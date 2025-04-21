"""
Test script to verify connection to OpenAI models via OpenRouter.
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get OpenRouter API key
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
if not openrouter_api_key:
    print("Error: OPENROUTER_API_KEY not found in .env file")
    sys.exit(1)

# Print key format information
print(f"OpenRouter API key format: {'Valid ✓' if openrouter_api_key.startswith('sk-or-') else 'Unusual format ⚠️'}")
print(f"Key prefix: {openrouter_api_key[:10]}...")

try:
    # Initialize the OpenAI client with OpenRouter configuration
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
    )
    
    print("\nSending test request to OpenRouter API (GPT-4-turbo model)...")
    
    # Test chat completion
    response = client.chat.completions.create(
        model="openai/gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'OpenRouter connection to GPT-4-turbo successful!'"}
        ],
        max_tokens=50,
        extra_headers={
            "HTTP-Referer": "https://ai-trading-bot.com",
            "X-Title": "AI Trading Bot"
        }
    )
    
    # Print the response
    print("\nResponse from OpenRouter (GPT-4-turbo):")
    print(f"Status: Success")
    print(f"Model: {response.model}")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"\nError connecting to OpenRouter API: {str(e)}")
    
# Now test with DeepSeek model
try:
    print("\nSending test request to OpenRouter API (DeepSeek model)...")
    
    # Test chat completion with DeepSeek
    response = client.chat.completions.create(
        model="deepseek/deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'OpenRouter connection to DeepSeek model successful!'"}
        ],
        max_tokens=50,
        extra_headers={
            "HTTP-Referer": "https://ai-trading-bot.com",
            "X-Title": "AI Trading Bot"
        }
    )
    
    # Print the response
    print("\nResponse from OpenRouter (DeepSeek):")
    print(f"Status: Success")
    print(f"Model: {response.model}")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"\nError connecting to DeepSeek via OpenRouter: {str(e)}")

print("\nTest completed.") 