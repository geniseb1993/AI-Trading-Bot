#!/usr/bin/env python
import requests
import json
import argparse
from datetime import datetime

def send_tradingview_alert(symbol="AAPL", interval="15m", price=0.0, strategy="Test Strategy", signal="BUY", message=None):
    """
    Send a test alert to the TradingView webhook endpoint
    """
    # Updated URL to point to the TradingView integration server on port 5003
    url = "http://localhost:5003/api/tradingview/webhook"
    
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
            
            # Check if a bot action was triggered
            if "alert_id" in response.json():
                print(f"Alert ID: {response.json()['alert_id']}")
                
            # Try to get the current bot status
            try:
                status_url = "http://localhost:5003/api/tradingview/bots/status"
                status_response = requests.get(status_url)
                if status_response.status_code == 200:
                    print("\nCurrent bot status:")
                    print(json.dumps(status_response.json(), indent=2))
            except Exception as e:
                print(f"Could not fetch bot status: {str(e)}")
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

def send_direct_bot_control(bot_id="dual_bot", action="start", symbol="AAPL", price=0.0, strategy="Test Strategy"):
    """
    Send a direct command to control a bot through the TradingView integration
    """
    url = "http://localhost:5003/api/tradingview/bot/control"
    
    # Create the payload
    payload = {
        "bot_id": bot_id,
        "action": action,
        "signal_data": {
            "symbol": symbol,
            "price": price,
            "strategy": strategy,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    # Send the request
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            print(f"Success! Bot control command sent for {bot_id}.")
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
    parser.add_argument("--direct", action="store_true", help="Use direct bot control instead of webhook")
    parser.add_argument("--bot", type=str, default="dual_bot", choices=["dual_bot", "autonomous_bot", "rsi_bot"], help="Bot ID (default: dual_bot)")
    parser.add_argument("--action", type=str, default="start", choices=["start", "stop"], help="Bot action (default: start)")
    
    args = parser.parse_args()
    
    # If price is 0, fetch the current price from technical data endpoint
    if args.price == 0.0:
        try:
            tech_url = f"http://localhost:5003/api/tradingview/symbols/technical-data?symbol={args.symbol}&interval={args.interval}"
            response = requests.get(tech_url)
            if response.status_code == 200:
                data = response.json()
                if "data" in data and "price" in data["data"]:
                    args.price = data["data"]["price"]
                    print(f"Fetched current price for {args.symbol}: {args.price}")
        except Exception as e:
            print(f"Could not fetch price: {str(e)}")
            args.price = 100.0  # Use a default price if fetch fails
    
    if args.direct:
        # Use direct bot control
        send_direct_bot_control(
            bot_id=args.bot,
            action=args.action,
            symbol=args.symbol,
            price=args.price,
            strategy=args.strategy
        )
    else:
        # Use webhook
        send_tradingview_alert(
            symbol=args.symbol,
            interval=args.interval,
            price=args.price,
            strategy=args.strategy,
            signal=args.signal,
            message=args.message
        ) 