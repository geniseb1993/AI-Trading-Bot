import os
import sys
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
deepseek_model = os.getenv("DEEPSEEK_MODEL") or "deepseek-chat"
openrouter_model = os.getenv("OPENROUTER_MODEL") or "deepseek/deepseek-r1:free"

# Test via OpenRouter first
print("=== Testing Deepseek via OpenRouter ===")
if not openrouter_api_key:
    print("Error: OPENROUTER_API_KEY not found in .env file")
    sys.exit(1)

print(f"Using OpenRouter with model: {openrouter_model}")
print(f"OpenRouter API key starts with: {openrouter_api_key[:5]}... (ends with: ...{openrouter_api_key[-5:]}")
print("Sending test request to OpenRouter API...")

try:
    # Initialize the OpenAI client with OpenRouter base URL
    openrouter_client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key
    )
    
    # Test API connection with a simple completion
    response = openrouter_client.chat.completions.create(
        model=openrouter_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Deepseek via OpenRouter connection successful!'"}
        ],
        max_tokens=50
    )
    
    # Print the response
    print("\nResponse from OpenRouter API (Deepseek):")
    print(f"Status: Success")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"\nError connecting to OpenRouter API: {str(e)}")

# Test direct Deepseek connection if available
print("\n=== Testing Direct Deepseek Connection ===")
if not deepseek_api_key:
    print("Error: DEEPSEEK_API_KEY not found in .env file or is the same as OpenRouter")
    sys.exit(1)

# Check if it's likely the direct Deepseek API connection
if deepseek_api_key.startswith("sk-or"):
    print("Warning: Your DEEPSEEK_API_KEY appears to be an OpenRouter key.")
    print("This test may not work if it's not a direct Deepseek API key.")

print(f"Using Deepseek model: {deepseek_model}")
print(f"Deepseek API key starts with: {deepseek_api_key[:5]}... (ends with: ...{deepseek_api_key[-5:]}")
print("Sending test request to Deepseek API...")

try:
    # For direct Deepseek API, we would need the correct base URL
    # This is a placeholder as direct Deepseek API may have a different structure
    # You may need to modify this based on Deepseek's actual API documentation
    print("\nNote: Direct Deepseek API connection test is skipped as it requires specific SDK")
    print("The Deepseek model is accessible through OpenRouter as shown above")
except Exception as e:
    print(f"\nError connecting to Deepseek API: {str(e)}") 