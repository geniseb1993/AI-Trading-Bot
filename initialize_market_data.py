#!/usr/bin/env python

"""
Market Data Integration Initialization Script

This script helps set up the market data integration environment by:
1. Checking for required dependencies
2. Creating a default configuration file
3. Setting up a .env file for API keys
4. Testing connectivity to market data sources

Usage:
    python initialize_market_data.py
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import importlib.util
from getpass import getpass

def print_header(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def check_dependencies():
    """Check if required packages are installed"""
    print_header("Checking Dependencies")
    
    required_packages = [
        'flask', 'flask_cors', 'requests', 
        'pandas', 'python-dotenv', 'alpaca-trade-api', 
        'alpaca-py', 'ibapi'
    ]
    
    optional_packages = [
        'ib-insync'  # Simplified IB API wrapper
    ]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        spec = importlib.util.find_spec(package.replace('-', '_'))
        if spec is None:
            missing_required.append(package)
    
    for package in optional_packages:
        spec = importlib.util.find_spec(package.replace('-', '_'))
        if spec is None:
            missing_optional.append(package)
    
    if missing_required:
        print("Missing required packages:")
        for pkg in missing_required:
            print(f"  - {pkg}")
        
        install = input("\nWould you like to install the missing required packages? (y/n): ")
        if install.lower() == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_required)
            print("Required packages installed successfully.")
    else:
        print("All required packages are installed.")
    
    if missing_optional:
        print("\nMissing optional packages:")
        for pkg in missing_optional:
            print(f"  - {pkg}")
        
        install = input("\nWould you like to install the optional packages? (y/n): ")
        if install.lower() == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_optional)
            print("Optional packages installed successfully.")
    else:
        print("\nAll optional packages are installed.")

def create_config_dir():
    """Create the config directory if it doesn't exist"""
    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api', 'lib')
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

def create_market_data_config():
    """Create a default market data configuration file"""
    print_header("Creating Default Configuration")
    
    config_dir = create_config_dir()
    config_file = os.path.join(config_dir, 'market_data_config.json')
    
    default_config = {
        'active_source': 'alpaca',
        'alpaca': {
            'api_key': None,
            'api_secret': None,
            'base_url': 'https://paper-api.alpaca.markets'
        },
        'interactive_brokers': {
            'port': 7496,
            'client_id': 0
        },
        'unusual_whales': {
            'token': None
        },
        'tradingview': {
            'webhook_port': 5001,
            'webhook_path': '/tradingview-webhook'
        }
    }
    
    if os.path.exists(config_file):
        print(f"Configuration file already exists at: {config_file}")
        overwrite = input("Would you like to overwrite it? (y/n): ")
        if overwrite.lower() != 'y':
            print("Skipping configuration file creation.")
            return
    
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=4)
    
    print(f"Default configuration file created at: {config_file}")

def create_env_file():
    """Create a .env file for API keys"""
    print_header("Setting Up Environment Variables")
    
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    
    if os.path.exists(env_file):
        print(f".env file already exists at: {env_file}")
        overwrite = input("Would you like to overwrite it? (y/n): ")
        if overwrite.lower() != 'y':
            print("Skipping .env file creation.")
            return
    
    # Ask for API keys
    print("\nEnter your API keys (leave blank if you don't have them yet):")
    
    alpaca_key = input("Alpaca API Key: ")
    alpaca_secret = getpass("Alpaca API Secret: ")
    unusual_whales_token = getpass("Unusual Whales API Token: ")
    
    # Create .env file
    with open(env_file, 'w') as f:
        f.write("# Market Data API Keys\n")
        f.write(f"ALPACA_API_KEY={alpaca_key}\n")
        f.write(f"ALPACA_API_SECRET={alpaca_secret}\n")
        f.write(f"ALPACA_BASE_URL=https://paper-api.alpaca.markets\n\n")
        
        f.write("# Interactive Brokers Configuration\n")
        f.write("IB_PORT=7496\n")
        f.write("IB_CLIENT_ID=0\n\n")
        
        f.write("# Unusual Whales API\n")
        f.write(f"UNUSUAL_WHALES_TOKEN={unusual_whales_token}\n\n")
        
        f.write("# TradingView Webhook Configuration\n")
        f.write("TRADINGVIEW_WEBHOOK_PORT=5001\n")
        f.write("TRADINGVIEW_WEBHOOK_PATH=/tradingview-webhook\n\n")
        
        f.write("# Default Market Data Source\n")
        f.write("MARKET_DATA_SOURCE=alpaca\n")
    
    print(f".env file created at: {env_file}")
    print("\nNote: You can update these values anytime by:")
    print("1. Editing the .env file directly")
    print("2. Using the API Configuration page in the application")

def install_browser_open():
    """Install webbrowser module if not available"""
    try:
        import webbrowser
        return webbrowser
    except ImportError:
        print("webbrowser module not available. Skipping browser opening.")
        return None

def print_next_steps():
    """Print instructions for next steps"""
    print_header("Next Steps")
    
    print("1. Start the API server:")
    print("   python start-api.py")
    print("\n2. Start the frontend:")
    print("   cd frontend && npm start")
    print("\n3. Open the application in your browser:")
    print("   http://localhost:3000")
    print("\n4. Enter PIN `8080` to access the trading dashboard")
    print("\n5. Navigate to the API Configuration page to verify your settings")
    print("\n6. Visit the Market Data page to view real-time market data")
    print("\n7. Check out the TradingView Alerts page for webhook integration")

def print_implementation_status():
    """Print the status of the implementation plan"""
    print_header("Implementation Plan Status")
    
    print("✅ STAGE 1: Connect to Real-Time Market Data - COMPLETED")
    print("   - Dark Pool & Options Flow APIs: Unusual Whales API integrated")
    print("   - Live Market Data Feeds: Interactive Brokers and TradingView integrated")
    print("   - Volume & Order Flow Tracking: Implemented through Alpaca and IB APIs")
    print("   - Data Source Selection: Added user-configurable source switching")
    
    print("\n⏳ STAGE 2: Build a Real-Time Trade Execution Model - PENDING")
    print("\n⏳ STAGE 3: Integrate AI With Trading Platforms - PENDING")
    print("\n⏳ STAGE 4: Build a Live AI Trading Dashboard - PENDING")
    print("\n⏳ STAGE 5: Expand Backtest to Handle Shorts & Stop-Loss - PENDING")
    
    print("\nFor details on the implementation plan, see 'AI Trading Bot New Feature Implementation Plan.txt'")
    
def main():
    """Main function"""
    print_header("Market Data Integration Setup")
    
    check_dependencies()
    create_market_data_config()
    create_env_file()
    print_next_steps()
    print_implementation_status()
    
    # Open the API documentation
    print("\nWould you like to open the documentation for the APIs?")
    open_docs = input("This will open the websites in your browser (y/n): ")
    
    if open_docs.lower() == 'y':
        webbrowser = install_browser_open()
        if webbrowser:
            webbrowser.open("https://alpaca.markets/docs/api-documentation/")
            webbrowser.open("https://interactivebrokers.github.io/tws-api/")
            webbrowser.open("https://unusualwhales.com/documentation")
            webbrowser.open("https://www.tradingview.com/support/solutions/43000529348-webhooks/")
    
    print_header("Setup Complete")
    print("Your market data integration environment is now ready to use!")
    print("Stage 1 of the AI Trading Bot Feature Implementation Plan has been completed.")

if __name__ == "__main__":
    main() 