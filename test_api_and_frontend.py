import requests
import json
import os
import sys
import pandas as pd
from datetime import datetime

# Configuration
API_URL = "http://localhost:5000/api"
FRONTEND_URL = "http://localhost:3000"
SIGNALS_ENDPOINT = f"{API_URL}/get-saved-signals"
API_TEST_ENDPOINT = f"{API_URL}/test"
DATA_DIR = "data"
BUY_SIGNALS_FILE = os.path.join(DATA_DIR, "buy_signals.csv")
SHORT_SIGNALS_FILE = os.path.join(DATA_DIR, "short_signals.csv")

def test_api_connection():
    """Test if the API server is running and accessible"""
    print("\n✅ TESTING API SERVER CONNECTION")
    try:
        response = requests.get(API_TEST_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"API Server is running: {data.get('message', 'No message')}")
            print(f"Environment: {data.get('environment', 'Unknown')}")
            print(f"Timestamp: {data.get('timestamp', 'Unknown')}")
            
            if data.get('success') == True:
                print("✅ API Server connection successful!")
                return True
            else:
                print("⚠️ API Server reported unsuccessful status")
                return False
        else:
            print(f"❌ API Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API Server - Connection refused")
        return False
    except Exception as e:
        print(f"❌ Error connecting to API Server: {str(e)}")
        return False

def test_frontend_connection():
    """Test if the frontend server is running and accessible"""
    print("\n✅ TESTING FRONTEND SERVER CONNECTION")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print(f"Frontend server is running and returned status code: {response.status_code}")
            print("✅ Frontend Server connection successful!")
            return True
        else:
            print(f"❌ Frontend Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Frontend Server - Connection refused")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Frontend Server: {str(e)}")
        return False

def verify_signal_files():
    """Verify that signal files exist and contain data"""
    print("\n✅ VERIFYING SIGNAL FILES")
    
    if not os.path.exists(DATA_DIR):
        print(f"❌ Data directory not found: {DATA_DIR}")
        return False
    
    buy_exists = os.path.exists(BUY_SIGNALS_FILE)
    short_exists = os.path.exists(SHORT_SIGNALS_FILE)
    
    if not buy_exists:
        print(f"❌ Buy signals file not found: {BUY_SIGNALS_FILE}")
    if not short_exists:
        print(f"❌ Short signals file not found: {SHORT_SIGNALS_FILE}")
    
    if not buy_exists or not short_exists:
        return False
    
    try:
        buy_df = pd.read_csv(BUY_SIGNALS_FILE)
        short_df = pd.read_csv(SHORT_SIGNALS_FILE)
        
        print(f"Buy signals file contains {len(buy_df)} records")
        print(f"Short signals file contains {len(short_df)} records")
        
        if len(buy_df) == 0 or len(short_df) == 0:
            print("⚠️ Warning: One or both signal files contain no records")
            return False
            
        # Check for required columns
        required_columns = ['symbol', 'signal_score', 'close', 'ema_9', 'ema_21', 'volume']
        
        for col in required_columns:
            if col not in buy_df.columns:
                print(f"❌ Buy signals file missing required column: {col}")
                return False
            if col not in short_df.columns:
                print(f"❌ Short signals file missing required column: {col}")
                return False
        
        print("✅ Signal files verified successfully!")
        return True
    except Exception as e:
        print(f"❌ Error reading signal files: {str(e)}")
        return False

def test_signals_api():
    """Test the signals API endpoint"""
    print("\n✅ TESTING SIGNALS API ENDPOINT")
    try:
        response = requests.get(SIGNALS_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            print(f"API Success: {data.get('success', False)}")
            print(f"Is mock data: {data.get('is_mock', False)}")
            
            if 'message' in data:
                print(f"Message: {data['message']}")
            
            buy_signals = data.get('buy_signals', [])
            short_signals = data.get('short_signals', [])
            
            print(f"Buy signals received: {len(buy_signals)}")
            print(f"Short signals received: {len(short_signals)}")
            
            if buy_signals and short_signals:
                # Show sample of first signal
                print("\nSample buy signal:")
                print(json.dumps(buy_signals[0], indent=2))
                
                print("\nSample short signal:")
                print(json.dumps(short_signals[0], indent=2))
                
                print("\n✅ Signals API endpoint working correctly!")
                return True
            else:
                print("⚠️ Warning: API returned empty signals arrays")
                return False
        else:
            print(f"❌ Signals API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Signals API - Connection refused")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Signals API: {str(e)}")
        return False

def generate_test_signals():
    """Generate test signals if no signals are available"""
    print("\n✅ GENERATING TEST SIGNALS")
    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created data directory: {DATA_DIR}")
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Generate buy signals
    buy_signals = pd.DataFrame({
        'date': [today] * 10,
        'symbol': ['SPY', 'AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMD', 'META', 'AMZN', 'GOOGL', 'QQQ'],
        'signal_score': [8.5, 7.9, 8.2, 8.7, 9.1, 8.8, 7.5, 8.3, 8.6, 9.2],
        'close': [525.66, 194.27, 371.61, 241.55, 104.49, 88.29, 502.31, 174.33, 153.33, 444.18],
        'ema_9': [520.50, 190.20, 375.10, 245.70, 106.20, 90.40, 510.60, 176.00, 155.80, 440.30],
        'ema_21': [515.30, 185.40, 378.90, 248.20, 108.60, 94.10, 520.30, 180.40, 158.20, 438.50],
        'volume': [83249030, 59669999, 21946406, 112255697, 396238244, 62156985, 18715162, 51791338, 28178029, 48812825]
    })
    
    # Generate short signals
    short_signals = pd.DataFrame({
        'date': [today] * 10,
        'symbol': ['IBM', 'INTC', 'BA', 'GE', 'XOM', 'CVX', 'PFE', 'MRK', 'VZ', 'T'],
        'signal_score': [-8.3, -9.1, -8.6, -8.9, -8.7, -9.4, -9.8, -7.5, -9.7, -7.6],
        'close': [238.57, 19.23, 156.47, 182.45, 104.19, 135.36, 22.04, 76.46, 43.61, 27.02],
        'ema_9': [240.20, 21.10, 155.30, 186.10, 106.50, 140.30, 24.20, 80.00, 43.80, 26.50],
        'ema_21': [242.60, 22.80, 153.20, 190.40, 110.30, 145.60, 25.40, 83.50, 44.10, 26.10],
        'volume': [4870268, 89311716, 6803289, 5128031, 13602717, 8630197, 37612871, 16546159, 17268517, 27831469]
    })
    
    # Save to CSV files
    buy_signals.to_csv(BUY_SIGNALS_FILE, index=False)
    short_signals.to_csv(SHORT_SIGNALS_FILE, index=False)
    
    print(f"Generated and saved {len(buy_signals)} buy signals to {BUY_SIGNALS_FILE}")
    print(f"Generated and saved {len(short_signals)} short signals to {SHORT_SIGNALS_FILE}")
    
    return True

def diagnose_frontend_issues():
    """Diagnose potential frontend issues"""
    print("\n📊 FRONTEND DIAGNOSIS")
    
    # Check for common frontend issues
    print("\nChecking potential issues:")
    
    # 1. Verify API proxy setup
    try:
        proxy_file = os.path.join("frontend", "src", "setupProxy.js")
        if os.path.exists(proxy_file):
            print("✅ setupProxy.js file exists")
            
            with open(proxy_file, 'r') as f:
                content = f.read()
                
                if '/api/get-saved-signals' in content:
                    print("✅ setupProxy.js contains signals endpoint configuration")
                else:
                    print("⚠️ setupProxy.js might be missing signals endpoint configuration")
                    
                if "createProxyMiddleware" in content:
                    print("✅ setupProxy.js uses createProxyMiddleware")
                else:
                    print("⚠️ setupProxy.js might not be using createProxyMiddleware")
        else:
            print("❌ setupProxy.js file missing")
    except Exception as e:
        print(f"❌ Error checking setupProxy.js: {str(e)}")
    
    # 2. Check Signals component
    try:
        signals_file = os.path.join("frontend", "src", "pages", "Signals.js")
        if os.path.exists(signals_file):
            print("✅ Signals.js file exists")
            
            with open(signals_file, 'r') as f:
                content = f.read()
                
                if "'/api/get-saved-signals'" in content or '"/api/get-saved-signals"' in content:
                    print("✅ Signals.js contains correct API endpoint path")
                else:
                    print("⚠️ Signals.js might have incorrect API endpoint path")
                    
                if "TradingViewIntegration" in content:
                    print("✅ Signals.js uses TradingViewIntegration service")
                else:
                    print("⚠️ Signals.js might not be using TradingViewIntegration service")
        else:
            print("❌ Signals.js file missing")
    except Exception as e:
        print(f"❌ Error checking Signals.js: {str(e)}")
    
    # 3. Network connectivity between frontend and backend
    print("\nNetwork connectivity check:")
    import socket
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(('localhost', 5000))
        if result == 0:
            print("✅ Port 5000 (backend) is open and accessible")
        else:
            print("❌ Port 5000 (backend) is closed or not accessible")
        s.close()
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(('localhost', 3000))
        if result == 0:
            print("✅ Port 3000 (frontend) is open and accessible")
        else:
            print("❌ Port 3000 (frontend) is closed or not accessible")
        s.close()
    except Exception as e:
        print(f"❌ Error checking network connectivity: {str(e)}")
    
    print("\nSuggested fixes:")
    print("1. Make sure both the backend server and frontend are running")
    print("2. Check browser console for any JavaScript errors")
    print("3. Verify that the fetch calls in Signals.js have proper error handling")
    print("4. Try using the test-signals-api.html to test API directly")
    print("5. Ensure CORS settings in the backend allow requests from frontend")

def main():
    """Main test function"""
    print("\n" + "="*50)
    print("🚀 API & FRONTEND INTEGRATION TEST")
    print("="*50)
    
    api_ok = test_api_connection()
    frontend_ok = test_frontend_connection()
    
    # If API server is running, test the signals endpoint
    if api_ok:
        files_ok = verify_signal_files()
        
        # If signal files are missing or invalid, generate test signals
        if not files_ok:
            print("\n⚠️ Signal files missing or invalid. Generating test signals...")
            generate_test_signals()
        
        # Test the signals API endpoint
        api_signals_ok = test_signals_api()
        
        if not api_signals_ok:
            print("\n⚠️ Issues detected with Signals API. Check server logs for details.")
    
    # If frontend is running, diagnose potential frontend issues
    if frontend_ok:
        diagnose_frontend_issues()
    
    # Summary
    print("\n" + "="*50)
    print("🏁 TEST SUMMARY")
    print("="*50)
    print(f"API Server: {'✅ Connected' if api_ok else '❌ Not connected'}")
    print(f"Frontend Server: {'✅ Connected' if frontend_ok else '❌ Not connected'}")
    
    if api_ok:
        print(f"Signal Files: {'✅ Valid' if verify_signal_files() else '❌ Invalid'}")
        print(f"Signals API: {'✅ Working' if test_signals_api() else '❌ Not working'}")
    
    print("\n📋 NEXT STEPS:")
    if not api_ok:
        print("- Start the API server using 'python minimal_flask_server.py'")
    if not frontend_ok:
        print("- Start the frontend server using 'cd frontend && npm start'")
    
    print("- Open test-signals-api.html in your browser to test the API directly")
    print("- Check browser console for JavaScript errors in the frontend")
    print("- Review server logs for any backend errors")
    
    print("\nTest completed at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    main() 