import requests
import json
import time
from datetime import datetime

# API endpoints
BASE_URL = "http://localhost:5000/api"
TRADINGVIEW_BASE = f"{BASE_URL}/tradingview"
FRONTEND_URL = "http://localhost:3000"

def test_tradingview_frontend_integration():
    """Test the integration between backend TradingView routes and frontend services"""
    print("\n==== TESTING TRADINGVIEW FRONTEND INTEGRATION ====\n")
    
    # 1. Check backend endpoints
    print("\n--- BACKEND ENDPOINTS TEST ---\n")
    
    endpoints = {
        "test": f"{TRADINGVIEW_BASE}/test",
        "alerts": f"{TRADINGVIEW_BASE}/alerts",
        "market_analysis": f"{TRADINGVIEW_BASE}/market/analysis",
        "technical_data": f"{TRADINGVIEW_BASE}/symbols/technical-data?symbol=AAPL&interval=1d"
    }
    
    for name, url in endpoints.items():
        try:
            print(f"Testing endpoint: {name}")
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Endpoint {name} is working")
                if name == "market_analysis":
                    if "analysis" in data and data.get("success") == True:
                        print(f"   Market analysis contains: {', '.join(data['analysis'].keys())}")
                    else:
                        print(f"   ⚠️ Market analysis format unexpected: {data.keys()}")
                elif name == "technical_data":
                    if "data" in data and data.get("success") == True:
                        indicators = data['data'].get('technical_indicators', {})
                        print(f"   Technical data contains indicators: {', '.join(indicators.keys()) if indicators else 'None'}")
                    else:
                        print(f"   ⚠️ Technical data format unexpected: {data.keys()}")
            else:
                print(f"❌ Endpoint {name} failed with status {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing endpoint {name}: {e}")
    
    # 2. Add a new webhook alert for testing
    print("\n--- ADDING WEBHOOK TEST ALERT ---\n")
    
    test_alert = {
        "symbol": "AMD",
        "strategy": "Price Breakout",
        "action": "BUY",
        "price": 159.87,
        "timestamp": datetime.now().isoformat(),
        "message": "AMD broke above resistance at $158",
        "interval": "4h"
    }
    
    try:
        webhook_url = f"{TRADINGVIEW_BASE}/webhook"
        print(f"Sending test alert to {webhook_url}")
        response = requests.post(webhook_url, json=test_alert)
        
        if response.status_code == 200:
            print(f"✅ Test alert sent successfully")
        else:
            print(f"❌ Failed to send test alert: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error sending test alert: {e}")
    
    # 3. Verify alert storage
    time.sleep(1)  # Allow processing time
    try:
        alerts_url = f"{TRADINGVIEW_BASE}/alerts"
        response = requests.get(alerts_url)
        
        if response.status_code == 200:
            alerts_data = response.json()
            alerts = alerts_data.get('alerts', [])
            amd_alerts = [a for a in alerts if a.get('symbol') == 'AMD']
            
            if amd_alerts:
                print(f"✅ AMD test alert found in stored alerts")
            else:
                print(f"❌ AMD test alert not found in stored alerts")
                
            print(f"Total alerts stored: {len(alerts)}")
        else:
            print(f"❌ Failed to retrieve alerts: {response.status_code}")
    except Exception as e:
        print(f"❌ Error retrieving alerts: {e}")
    
    # 4. Test frontend API compatibility
    print("\n--- TESTING FRONTEND COMPATIBILITY ---\n")
    
    # Test the API endpoint used by TradingViewIntegration.js
    frontend_endpoints = [
        {"name": "Market Analysis", "url": f"{BASE_URL}/market-data/analysis"},
        {"name": "AI Signals", "url": f"{BASE_URL}/market/ai_signals/SPY"},
        {"name": "TradingView Webhooks", "url": f"{BASE_URL}/market-data/tradingview/webhooks"}
    ]
    
    for endpoint in frontend_endpoints:
        try:
            print(f"Testing frontend endpoint: {endpoint['name']}")
            response = requests.get(endpoint['url'])
            
            if response.status_code == 200:
                print(f"✅ Frontend endpoint {endpoint['name']} is accessible")
                # Check if response format is as expected
                try:
                    data = response.json()
                    if 'success' in data:
                        print(f"   Response status: {'✅ Success' if data['success'] else '❌ Failed'}")
                    else:
                        print(f"   ⚠️ Response doesn't include success field")
                except:
                    print(f"   ⚠️ Response is not valid JSON")
            else:
                print(f"❌ Frontend endpoint {endpoint['name']} returned {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing {endpoint['name']}: {e}")
    
    print("\n==== TRADINGVIEW FRONTEND INTEGRATION TEST COMPLETE ====\n")
    print("Summary:")
    print("1. Verified backend TradingView API endpoints")
    print("2. Tested webhook alert submission")
    print("3. Verified alert storage and retrieval")
    print("4. Checked frontend API compatibility")

if __name__ == "__main__":
    test_tradingview_frontend_integration() 