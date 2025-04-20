#!/usr/bin/env python
import requests
import json
import argparse
from datetime import datetime

def send_tradingview_alert(symbol="AAPL", interval="15m", price=0.0, strategy="Test Strategy", signal="BUY", message=None):
    """
    Send a test alert to the TradingView webhook endpoint
    """
    url = "http://localhost:5000/api/tradingview/webhook"
    
    # Create the payload
    payload = {
        "symbol": symbol,
        "interval": interval,
        "price": price,
        "strategy": strategy,
        "signal": signal,
        "timestamp": datetime.now().isoformat()
    }
    
    # Add message if provided
    if message:
        payload["message"] = message
    else:
        payload["message"] = f"{signal} signal for {symbol} at {price} on {interval} timeframe using {strategy}"
    
    # Send the request
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            print(f"Success! Alert sent for {symbol}.")
            print(f"Response: {response.json()}")
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send test alerts to TradingView webhook")
    parser.add_argument("--symbol", type=str, default="AAPL", help="Stock symbol (default: AAPL)")
    parser.add_argument("--interval", type=str, default="15m", help="Time interval (default: 15m)")
    parser.add_argument("--price", type=float, default=0.0, help="Current price (default: 0.0)")
    parser.add_argument("--strategy", type=str, default="Test Strategy", help="Strategy name (default: Test Strategy)")
    parser.add_argument("--signal", type=str, default="BUY", choices=["BUY", "SELL", "NEUTRAL"], help="Signal type (default: BUY)")
    parser.add_argument("--message", type=str, help="Custom alert message (optional)")
    
    args = parser.parse_args()
    
    # If price is 0, fetch the current price from technical data endpoint
    if args.price == 0.0:
        try:
            tech_url = f"http://localhost:5000/api/tradingview/symbols/technical-data?symbol={args.symbol}&interval={args.interval}"
            response = requests.get(tech_url)
            if response.status_code == 200:
                data = response.json()
                if "price" in data:
                    args.price = data["price"]
                    print(f"Fetched current price for {args.symbol}: {args.price}")
        except Exception as e:
            print(f"Could not fetch price: {str(e)}")
            args.price = 100.0  # Use a default price if fetch fails
    
    send_tradingview_alert(
        symbol=args.symbol,
        interval=args.interval,
        price=args.price,
        strategy=args.strategy,
        signal=args.signal,
        message=args.message
    ) 