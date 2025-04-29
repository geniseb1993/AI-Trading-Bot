import requests
import json
import time
from datetime import datetime
import argparse

# API endpoints
API_BASE_URL = "http://localhost:5000"
STATUS_ENDPOINT = f"{API_BASE_URL}/api/bot/status"
START_BOT_ENDPOINT = lambda bot_type: f"{API_BASE_URL}/api/bot/{bot_type}/start"
STOP_BOT_ENDPOINT = lambda bot_type: f"{API_BASE_URL}/api/bot/{bot_type}/stop"
RESET_BOT_ENDPOINT = lambda bot_type: f"{API_BASE_URL}/api/bot/{bot_type}/reset"
CONFIG_ENDPOINT = lambda bot_type: f"{API_BASE_URL}/api/bot/{bot_type}/config"
LOGS_ENDPOINT = lambda bot_type: f"{API_BASE_URL}/api/bot/{bot_type}/logs"
HEALTH_ENDPOINT = f"{API_BASE_URL}/api/health"

# Define known bot types
KNOWN_BOTS = ['autonomous_bot', 'rsi_bot', 'dual_bot']

class BotAPITester:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {
            "health_check": None,
            "status_check": None,
            "bot_operations": {},
            "config_operations": {},
            "log_operations": {}
        }
    
    def log(self, message):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(message)
    
    def test_health_endpoint(self):
        """Test the health endpoint of the API"""
        print("\n=== Testing API Health ===")
        try:
            response = requests.get(HEALTH_ENDPOINT)
            status_code = response.status_code
            
            if status_code == 200:
                data = response.json()
                print(f"API is healthy: {data}")
                self.results["health_check"] = True
                return True
            else:
                print(f"API health check failed with status code: {status_code}")
                print(f"Response: {response.text}")
                self.results["health_check"] = False
                return False
        except Exception as e:
            print(f"Error connecting to API: {str(e)}")
            self.results["health_check"] = False
            return False
    
    def test_status_endpoint(self):
        """Test the status endpoint of the API"""
        print("\n=== Testing Bot Status Endpoint ===")
        try:
            response = requests.get(STATUS_ENDPOINT)
            status_code = response.status_code
            
            if status_code == 200:
                data = response.json()
                print(f"Successfully retrieved bot status:")
                for bot_type, status in data.items():
                    bot_status = status.get('status', 'unknown')
                    last_active = status.get('last_active', 'N/A')
                    print(f"- {bot_type}: {bot_status} (Last active: {last_active})")
                
                self.results["status_check"] = True
                return data
            else:
                print(f"Status check failed with status code: {status_code}")
                print(f"Response: {response.text}")
                self.results["status_check"] = False
                return {}
        except Exception as e:
            print(f"Error retrieving bot status: {str(e)}")
            self.results["status_check"] = False
            return {}
    
    def test_bot_control(self, bot_type):
        """Test starting and stopping a specific bot"""
        print(f"\n=== Testing Bot Control for {bot_type} ===")
        self.results["bot_operations"][bot_type] = {
            "start": False,
            "stop": False,
            "reset": False
        }
        
        # Get initial status
        initial_status = self.get_bot_status(bot_type)
        initial_state = initial_status.get('status', 'unknown')
        print(f"Initial status: {initial_state}")
        
        # Test stop operation
        print(f"\nTesting stop operation for {bot_type}...")
        stop_result = self.stop_bot(bot_type)
        time.sleep(1)  # Wait for status to update
        
        # Verify the bot is stopped
        after_stop_status = self.get_bot_status(bot_type)
        after_stop_state = after_stop_status.get('status', 'unknown')
        print(f"Status after stop attempt: {after_stop_state}")
        
        if after_stop_state == 'inactive':
            print(f"✓ Successfully stopped {bot_type}")
            self.results["bot_operations"][bot_type]["stop"] = True
        else:
            print(f"✗ Failed to stop {bot_type}")
        
        # Test start operation
        print(f"\nTesting start operation for {bot_type}...")
        start_result = self.start_bot(bot_type)
        time.sleep(1)  # Wait for status to update
        
        # Verify the bot is started
        after_start_status = self.get_bot_status(bot_type)
        after_start_state = after_start_status.get('status', 'unknown')
        print(f"Status after start attempt: {after_start_state}")
        
        if after_start_state == 'active':
            print(f"✓ Successfully started {bot_type}")
            self.results["bot_operations"][bot_type]["start"] = True
        else:
            print(f"✗ Failed to start {bot_type}")
        
        # Test reset operation
        print(f"\nTesting reset operation for {bot_type}...")
        reset_result = self.reset_bot(bot_type)
        time.sleep(1)  # Wait for status to update
        
        # Verify the bot was reset (usually it should be active after reset)
        after_reset_status = self.get_bot_status(bot_type)
        after_reset_state = after_reset_status.get('status', 'unknown')
        print(f"Status after reset attempt: {after_reset_state}")
        
        if reset_result:
            print(f"✓ Successfully reset {bot_type}")
            self.results["bot_operations"][bot_type]["reset"] = True
        else:
            print(f"✗ Failed to reset {bot_type}")
        
        # Restore original state
        if initial_state == 'active' and after_reset_state != 'active':
            self.start_bot(bot_type)
        elif initial_state == 'inactive' and after_reset_state != 'inactive':
            self.stop_bot(bot_type)
    
    def test_config_operations(self, bot_type):
        """Test configuration operations for a specific bot"""
        print(f"\n=== Testing Configuration Operations for {bot_type} ===")
        self.results["config_operations"][bot_type] = {
            "get": False,
            "update": False
        }
        
        # Get current configuration
        print(f"Getting current configuration for {bot_type}...")
        try:
            response = requests.get(CONFIG_ENDPOINT(bot_type))
            if response.status_code == 200:
                config = response.json()
                print(f"Successfully retrieved configuration for {bot_type}")
                self.log(f"Configuration: {json.dumps(config, indent=2)}")
                self.results["config_operations"][bot_type]["get"] = True
                
                # Test updating configuration (we'll just update a comment field)
                test_update = {
                    "comment": f"Test update at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
                
                print(f"Testing configuration update for {bot_type}...")
                update_response = requests.post(
                    CONFIG_ENDPOINT(bot_type),
                    json=test_update
                )
                
                if update_response.status_code == 200:
                    print(f"✓ Successfully updated configuration for {bot_type}")
                    self.results["config_operations"][bot_type]["update"] = True
                else:
                    print(f"✗ Failed to update configuration: {update_response.text}")
            else:
                print(f"Failed to get configuration: {response.text}")
        except Exception as e:
            print(f"Error during configuration operations: {str(e)}")
    
    def test_log_operations(self, bot_type):
        """Test log retrieval for a specific bot"""
        print(f"\n=== Testing Log Operations for {bot_type} ===")
        self.results["log_operations"][bot_type] = False
        
        try:
            response = requests.get(LOGS_ENDPOINT(bot_type))
            if response.status_code == 200:
                logs = response.json()
                print(f"Successfully retrieved logs for {bot_type}")
                log_count = len(logs) if isinstance(logs, list) else 'N/A'
                print(f"Retrieved {log_count} log entries")
                self.results["log_operations"][bot_type] = True
            else:
                print(f"Failed to get logs: {response.text}")
        except Exception as e:
            print(f"Error during log operations: {str(e)}")
    
    def get_bot_status(self, bot_type=None):
        """Get the current status of all bots or a specific bot"""
        try:
            response = requests.get(STATUS_ENDPOINT)
            if response.status_code == 200:
                data = response.json()
                if bot_type:
                    return data.get(bot_type, {})
                return data
            return {}
        except Exception as e:
            self.log(f"Error getting bot status: {str(e)}")
            return {}
    
    def start_bot(self, bot_type):
        """Start a specific bot"""
        try:
            response = requests.post(START_BOT_ENDPOINT(bot_type))
            return response.status_code == 200
        except Exception as e:
            self.log(f"Error starting bot: {str(e)}")
            return False
    
    def stop_bot(self, bot_type):
        """Stop a specific bot"""
        try:
            response = requests.post(STOP_BOT_ENDPOINT(bot_type))
            return response.status_code == 200
        except Exception as e:
            self.log(f"Error stopping bot: {str(e)}")
            return False
    
    def reset_bot(self, bot_type):
        """Reset a specific bot"""
        try:
            response = requests.post(RESET_BOT_ENDPOINT(bot_type))
            return response.status_code == 200
        except Exception as e:
            self.log(f"Error resetting bot: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests for the API"""
        start_time = datetime.now()
        print(f"Starting API tests at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test API health
        if not self.test_health_endpoint():
            print("API health check failed. Aborting further tests.")
            return
        
        # Test status endpoint
        status_data = self.test_status_endpoint()
        
        # Test each bot
        for bot_type in KNOWN_BOTS:
            if bot_type in status_data:
                # Test bot control operations
                self.test_bot_control(bot_type)
                
                # Test configuration operations
                self.test_config_operations(bot_type)
                
                # Test log operations
                self.test_log_operations(bot_type)
            else:
                print(f"\nSkipping tests for {bot_type} as it's not found in the status response")
        
        # Print test summary
        self.print_summary()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"\nTests completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total duration: {duration:.2f} seconds")
    
    def print_summary(self):
        """Print a summary of all test results"""
        print("\n====== TEST SUMMARY ======")
        
        # Health check
        health_status = "✓ PASSED" if self.results["health_check"] else "✗ FAILED"
        print(f"API Health Check: {health_status}")
        
        # Status check
        status_status = "✓ PASSED" if self.results["status_check"] else "✗ FAILED"
        print(f"Bot Status Endpoint: {status_status}")
        
        # Bot operations
        print("\nBot Control Operations:")
        for bot_type, operations in self.results["bot_operations"].items():
            print(f"  {bot_type}:")
            for operation, success in operations.items():
                status = "✓ PASSED" if success else "✗ FAILED"
                print(f"    - {operation}: {status}")
        
        # Config operations
        print("\nConfiguration Operations:")
        for bot_type, operations in self.results["config_operations"].items():
            print(f"  {bot_type}:")
            for operation, success in operations.items():
                status = "✓ PASSED" if success else "✗ FAILED"
                print(f"    - {operation}: {status}")
        
        # Log operations
        print("\nLog Operations:")
        for bot_type, success in self.results["log_operations"].items():
            status = "✓ PASSED" if success else "✗ FAILED"
            print(f"  {bot_type}: {status}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Bot Management API")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--bot", "-b", help="Test only a specific bot type")
    args = parser.parse_args()
    
    tester = BotAPITester(verbose=args.verbose)
    
    if args.bot:
        if args.bot in KNOWN_BOTS:
            # Test API health
            if tester.test_health_endpoint():
                # Test only the specified bot
                tester.test_bot_control(args.bot)
                tester.test_config_operations(args.bot)
                tester.test_log_operations(args.bot)
                tester.print_summary()
        else:
            print(f"Unknown bot type: {args.bot}")
            print(f"Available bot types: {', '.join(KNOWN_BOTS)}")
    else:
        # Run all tests
        tester.run_all_tests() 