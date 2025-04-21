#!/usr/bin/env python3
"""
API Connectivity Check Script
This script verifies that the API server is running and accessible,
with detailed diagnostics and helpful error messages.
"""
import sys
import os
import json
import time
import argparse
import subprocess
import requests
from urllib.parse import urljoin
import platform

# Default API configurations
DEFAULT_API_HOST = "localhost"
DEFAULT_API_PORT = 5000
DEFAULT_API_BASE_URL = f"http://{DEFAULT_API_HOST}:{DEFAULT_API_PORT}"
DEFAULT_TIMEOUT = 5  # seconds

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def colorize(text, color):
    """Add color to terminal output if supported"""
    if sys.stdout.isatty() and platform.system() != "Windows":
        return f"{color}{text}{Colors.END}"
    return text

def check_api_health(base_url, endpoint="/api/health", timeout=DEFAULT_TIMEOUT):
    """Check if the API is healthy"""
    try:
        url = urljoin(base_url, endpoint)
        print(f"Checking API health at: {url}")
        
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        status = data.get('status', 'unknown')
        
        print(colorize(f"API Status: {status}", Colors.GREEN if status == "healthy" else Colors.YELLOW))
        print(f"Response time: {response.elapsed.total_seconds():.3f} seconds")
        
        return data
    except requests.exceptions.Timeout:
        print(colorize("Error: API request timed out", Colors.RED))
        return None
    except requests.exceptions.ConnectionError:
        print(colorize("Error: Could not connect to API", Colors.RED))
        print(f"Make sure the API server is running at {base_url}")
        return None
    except requests.exceptions.HTTPError as e:
        print(colorize(f"Error: HTTP error occurred: {e}", Colors.RED))
        return None
    except requests.exceptions.RequestException as e:
        print(colorize(f"Error: Request failed: {e}", Colors.RED))
        return None
    except json.JSONDecodeError:
        print(colorize("Error: Invalid JSON response from API", Colors.RED))
        return None

def check_detailed_health(base_url, timeout=DEFAULT_TIMEOUT):
    """Get detailed health information from the API"""
    try:
        url = urljoin(base_url, "/api/health/detailed")
        print(f"Fetching detailed health information from: {url}")
        
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        
        print("\n" + colorize("=== Detailed Health Information ===", Colors.BOLD))
        
        # Print system info
        if 'system' in data:
            system = data['system']
            print(colorize("\nSystem Information:", Colors.BLUE))
            print(f"  Platform: {system.get('platform', 'Unknown')} {system.get('platform_release', '')}")
            print(f"  Python version: {system.get('python_version', 'Unknown').split()[0]}")
            print(f"  Memory usage: {system.get('process_memory_usage_mb', 'Unknown')} MB")
        
        # Print component status
        if 'components' in data:
            components = data['components']
            print(colorize("\nComponent Status:", Colors.BLUE))
            for component, status in components.items():
                status_text = "Available" if status else "Not Available"
                status_color = Colors.GREEN if status else Colors.RED
                print(f"  {component}: {colorize(status_text, status_color)}")
        
        return data
    except Exception as e:
        print(colorize(f"Error fetching detailed health information: {e}", Colors.RED))
        return None

def check_bot_status(base_url, timeout=DEFAULT_TIMEOUT):
    """Check the status of trading bots"""
    try:
        url = urljoin(base_url, "/api/bot/status")
        print(f"Checking bot status at: {url}")
        
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        
        print("\n" + colorize("=== Bot Status ===", Colors.BOLD))
        
        # Check each bot's status
        for bot_type, bot_data in data.items():
            bot_status = bot_data.get('status', False)
            status_text = "Running" if bot_status else "Stopped"
            status_color = Colors.GREEN if bot_status else Colors.YELLOW
            
            print(f"\n{colorize(bot_type, Colors.BLUE)}:")
            print(f"  Status: {colorize(status_text, status_color)}")
            
            if 'last_update' in bot_data:
                print(f"  Last update: {bot_data['last_update']}")
            
            if 'error' in bot_data:
                print(f"  Error: {colorize(bot_data['error'], Colors.RED)}")
        
        return data
    except Exception as e:
        print(colorize(f"Error checking bot status: {e}", Colors.RED))
        return None

def check_api_running(host=DEFAULT_API_HOST, port=DEFAULT_API_PORT):
    """Check if something is listening on the API port"""
    import socket
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    sock.close()
    
    if result == 0:
        print(colorize(f"Port {port} is open - API server appears to be running", Colors.GREEN))
        return True
    else:
        print(colorize(f"Port {port} is not open - API server may not be running", Colors.RED))
        return False

def start_api_server():
    """Attempt to start the API server"""
    print("Attempting to start API server...")
    
    try:
        # Use a non-blocking subprocess
        if platform.system() == "Windows":
            process = subprocess.Popen(["python", "run_api.py"], 
                                      creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            process = subprocess.Popen(["python", "run_api.py"], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE)
        
        # Give it some time to start
        print("Waiting for API server to start...")
        time.sleep(5)
        
        # Check if it's running
        if check_api_running():
            print(colorize("API server successfully started!", Colors.GREEN))
            return True
        else:
            print(colorize("Failed to start API server", Colors.RED))
            return False
            
    except Exception as e:
        print(colorize(f"Error starting API server: {e}", Colors.RED))
        return False

def main():
    parser = argparse.ArgumentParser(description="Check API connectivity")
    parser.add_argument("--host", default=DEFAULT_API_HOST, help=f"API host (default: {DEFAULT_API_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_API_PORT, help=f"API port (default: {DEFAULT_API_PORT})")
    parser.add_argument("--start", action="store_true", help="Try to start the API server if not running")
    parser.add_argument("--detailed", action="store_true", help="Show detailed health information")
    parser.add_argument("--bots", action="store_true", help="Check bot status")
    
    args = parser.parse_args()
    
    base_url = f"http://{args.host}:{args.port}"
    
    print(colorize("=== API Connectivity Check ===", Colors.BOLD))
    print(f"Checking API at: {base_url}")
    
    # Check if API is running
    api_running = check_api_running(args.host, args.port)
    
    if not api_running and args.start:
        api_running = start_api_server()
    
    if api_running:
        # Check API health
        health_data = check_api_health(base_url)
        
        if health_data and args.detailed:
            detailed_data = check_detailed_health(base_url)
        
        if health_data and args.bots:
            bot_data = check_bot_status(base_url)
        
        if health_data:
            print("\n" + colorize("✓ API connectivity check passed", Colors.GREEN))
            return 0
    else:
        print("\n" + colorize("✗ API connectivity check failed", Colors.RED))
        print("\nTroubleshooting tips:")
        print("1. Make sure the API server is running")
        print("2. Check logs for errors")
        print("3. Try running 'python run_api.py' directly")
        print("4. Verify that port 5000 is not blocked by firewall or used by another application")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 