#!/usr/bin/env python
import requests
import json
import time
from datetime import datetime

def test_tradingview_webhook():
    """Test sending webhook alerts to the TradingView webhook endpoint"""
    url = "http://localhost:5003/api/tradingview/webhook"
    
    # Create test alerts
    alerts = [
        {
            "symbol": "SPY",
            "interval": "15m",
            "price": 452.75,
            "strategy": "EMA Crossover",
            "signal": "BUY",
            "message": "SPY: Bullish EMA crossover detected",
            "timestamp": datetime.now().isoformat()
        },
        {
            "symbol": "QQQ",
            "interval": "1h",
            "price": 378.25,
            "strategy": "RSI Divergence",
            "signal": "SELL",
            "message": "QQQ: Bearish RSI divergence detected",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    print("\n=== Testing TradingView Webhook Endpoint ===")
    
    # Send each alert
    for alert in alerts:
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=alert, headers=headers)
            
            print(f"Sent alert for {alert['symbol']} ({alert['signal']}):")
            if response.status_code == 200:
                print(f"  Success! Response: {response.json()}")
            else:
                print(f"  Error: Status code {response.status_code}")
                print(f"  Response: {response.text}")
        except Exception as e:
            print(f"  Exception: {str(e)}")
    
    # Wait a moment for the alerts to be processed
    time.sleep(1)
    
    return True

def test_tradingview_alerts():
    """Test retrieving TradingView webhook alerts"""
    url = "http://localhost:5003/api/tradingview/alerts"
    
    print("\n=== Testing TradingView Alerts Retrieval ===")
    
    try:
        # Get all alerts
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Retrieved {data.get('count', 0)} alerts:")
            for alert in data.get('alerts', []):
                print(f"  {alert.get('symbol')}: {alert.get('signal')} at {alert.get('price')}")
        else:
            print(f"Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            
        # Test filtering by symbol
        symbol = "SPY"
        response = requests.get(f"{url}?symbol={symbol}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nRetrieved {data.get('count', 0)} alerts for {symbol}")
        else:
            print(f"Error filtering by symbol: {response.status_code}")
    except Exception as e:
        print(f"Exception: {str(e)}")
    
    return True

def test_technical_indicators():
    """Test retrieving technical indicators for a symbol"""
    # Test symbols
    symbols = ["SPY", "AAPL", "MSFT", "QQQ"]
    
    print("\n=== Testing Technical Indicators Endpoint ===")
    
    for symbol in symbols:
        url = f"http://localhost:5003/api/tradingview/symbols/technical-data?symbol={symbol}"
        
        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    tech_data = data.get('data', {})
                    print(f"{symbol} Technical Data:")
                    print(f"  Price: {tech_data.get('price')}")
                    print(f"  RSI: {tech_data.get('technical_indicators', {}).get('rsi')}")
                    
                    # Check if we're using real or simulated data
                    if tech_data.get('is_simulated'):
                        print(f"  [Using simulated data]")
                    else:
                        print(f"  [Using real market data]")
                        
                    # Check moving averages
                    ma = tech_data.get('technical_indicators', {}).get('moving_averages', {})
                    print(f"  SMA 50: {ma.get('sma_50')}")
                    print(f"  EMA 9: {ma.get('ema_9')}")
                else:
                    print(f"{symbol}: Error in response - {data.get('message')}")
            else:
                print(f"{symbol}: Error - Status code {response.status_code}")
        except Exception as e:
            print(f"{symbol}: Exception - {str(e)}")
    
    return True

def test_market_analysis():
    """Test retrieving comprehensive market analysis"""
    url = "http://localhost:5003/api/tradingview/market/analysis"
    
    print("\n=== Testing Market Analysis Endpoint ===")
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                analysis = data.get('analysis', {})
                
                # Print major indices
                indices = analysis.get('major_indices', [])
                print("Major Indices:")
                for idx in indices:
                    print(f"  {idx.get('name', '')} ({idx.get('symbol', '')}): {idx.get('price')} ({idx.get('change')}%)")
                
                # Print sentiment
                sentiment = analysis.get('market_sentiment', {})
                print("\nMarket Sentiment:")
                print(f"  Fear & Greed Index: {sentiment.get('fear_greed_index')} - {sentiment.get('sentiment')}")
                print(f"  Market Trend: {sentiment.get('overall_market_trend')}")
                print(f"  Strongest Sector: {sentiment.get('strongest_sector')}")
                print(f"  Weakest Sector: {sentiment.get('weakest_sector')}")
            else:
                print(f"Error in response: {data.get('message')}")
        else:
            print(f"Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception: {str(e)}")
    
    return True

if __name__ == "__main__":
    print("===== TradingView Integration Test =====")
    print(f"Starting tests at {datetime.now().isoformat()}")
    
    # Test all endpoints
    test_tradingview_webhook()
    test_tradingview_alerts()
    test_technical_indicators()
    test_market_analysis()
    
    print("\n===== All tests completed =====") 