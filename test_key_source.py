import os
import sys
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# The key we want to test
api_key = os.getenv("OPENAI_API_KEY")

print(f"Testing API key: {api_key[:10]}...")
print("First, trying with OpenAI API...")

try:
    # Try with OpenAI
    openai_client = openai.OpenAI(api_key=api_key)
    response = openai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "user", "content": "Say 'This key works with OpenAI'"}
        ],
        max_tokens=20
    )
    print("Success with OpenAI API!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"Failed with OpenAI API: {str(e)}")
    
print("\nNow trying with OpenRouter API...")

try:
    # Try with OpenRouter
    openrouter_client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "https://ai-trading-bot.com", 
            "X-Title": "AI Trading Bot"
        }
    )
    
    response = openrouter_client.chat.completions.create(
        model="openai/gpt-3.5-turbo", # Using a cheaper model for testing
        messages=[
            {"role": "user", "content": "Say 'This key works with OpenRouter'"}
        ],
        max_tokens=20
    )
    print("Success with OpenRouter API!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"Failed with OpenRouter API: {str(e)}")

print("\nConclusion:")
print("Based on these tests, your key appears to be:")
print("- An OpenAI key that needs proper configuration, or")
print("- An OpenRouter key with 'sk-proj-' format")
print("\nRecommendation:")
print("1. Double-check that you got this key from platform.openai.com/api-keys")
print("2. If it's from OpenRouter, you should use it as OPENROUTER_API_KEY in your .env file")
print("3. Get a proper OpenAI key for the OPENAI_API_KEY field") 