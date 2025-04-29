#!/usr/bin/env python
"""
Start script for the TradingView integration server
"""
import os
import sys
import subprocess
import argparse
import time

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description='Start the TradingView integration server')
    parser.add_argument('--port', type=int, default=5003, help='Port to run the server on (default: 5003)')
    args = parser.parse_args()
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the script directory
    os.chdir(script_dir)
    
    # Command to run the server
    cmd = [sys.executable, 'tradingview_server.py']
    
    # Set environment variable for the port
    env = os.environ.copy()
    env['TRADINGVIEW_PORT'] = str(args.port)
    
    print(f"Starting TradingView integration server on port {args.port}...")
    
    # Run the server
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nTradingView server stopped.")
    except Exception as e:
        print(f"\nError starting TradingView server: {e}")
        sys.exit(1)

def start_server():
    """Start the TradingView integration server"""
    # Print startup message
    print("Starting TradingView Integration Server...")
    
    # Command to run the server
    server_script = os.path.join(os.path.dirname(__file__), "tradingview_integration.py")
    
    try:
        # Start the server process
        process = subprocess.Popen([sys.executable, server_script])
        
        # Wait a moment for the server to start
        time.sleep(2)
        
        # Print success message
        print("TradingView Integration Server started on port 5003")
        print("")
        print("Test endpoints:")
        print("- http://localhost:5003/api/test")
        print("- http://localhost:5003/api/tradingview/alerts")
        print("- http://localhost:5003/api/tradingview/symbols/technical-data?symbol=SPY")
        print("- http://localhost:5003/api/tradingview/market/analysis")
        
        return process
    except Exception as e:
        print(f"Error starting TradingView Integration Server: {str(e)}")
        return None

if __name__ == "__main__":
    main()
    
    try:
        # Keep the script running
        print("\nPress Ctrl+C to stop the server...")
        process.wait()
    except KeyboardInterrupt:
        print("\nStopping TradingView Integration Server...")
        process.terminate()
        print("Server stopped.") 