import os
import sys
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL") or "gpt-4-turbo"

# Validate API key
if not api_key:
    print("Error: OPENAI_API_KEY not found in .env file")
    print("Please add your OpenAI API key to the .env file")
    print("Get your API key from: https://platform.openai.com/api-keys")
    sys.exit(1)

# Check API key format
valid_prefixes = ["sk-", "sk-proj-", "sk-None-", "sk-svcacct-"]
is_valid_prefix = any(api_key.startswith(prefix) for prefix in valid_prefixes)

if not is_valid_prefix:
    print("Error: Invalid OpenAI API key format")
    print(f"OpenAI API keys should start with one of: {', '.join(valid_prefixes)}")
    print("Get a proper OpenAI key from: https://platform.openai.com/api-keys")
    sys.exit(1)

print(f"Testing OpenAI connection with model: {model}")
print(f"API key format: {'Valid ✓' if is_valid_prefix else 'Invalid ✗'}")
if api_key.startswith("sk-proj-"):
    print("Using a Project API key (newer format)")
print("Sending test request to OpenAI API...")

try:
    # Initialize the OpenAI client
    client = openai.OpenAI(api_key=api_key)
    
    # Test API connection with a simple completion
    print("Testing chat completion...")
    chat_response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'OpenAI API connection successful!'"}
        ],
        max_tokens=50
    )
    
    # Print the response
    print("\nResponse from OpenAI Chat API:")
    print(f"Status: Success")
    print(f"Response: {chat_response.choices[0].message.content}")
    
    # Test the newer responses API if using a 4.1 model
    if "gpt-4.1" in model:
        print("\nTesting newer responses API...")
        response = client.responses.create(
            model=model,
            input="Tell me a three sentence bedtime story about a unicorn."
        )
        
        print("\nResponse from OpenAI Responses API:")
        print(f"Status: Success") 
        print(f"Model: {response.model}")
        
        # Get the text from the first message
        if hasattr(response, 'output') and len(response.output) > 0:
            message = response.output[0]
            if hasattr(message, 'content') and len(message.content) > 0:
                content = message.content[0]
                if hasattr(content, 'text'):
                    print(f"Text: {content.text}")
    
except openai.AuthenticationError as e:
    print("\nAuthentication Error:")
    print("Your API key is invalid or expired.")
    print("Please get a new API key from: https://platform.openai.com/api-keys")
    print(f"Error details: {str(e)}")
    
except openai.RateLimitError:
    print("\nRate Limit Error:")
    print("You've exceeded your rate limit. Please try again later.")
    
except openai.APIConnectionError:
    print("\nConnection Error:")
    print("Could not connect to the OpenAI API. Please check your internet connection.")
    
except Exception as e:
    print(f"\nError connecting to OpenAI API: {str(e)}") 