"""
Simple script to test TradingView routes
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys

# Print current working directory for debugging
print("Current Working Directory:", os.getcwd())

# Create Flask app
app = Flask(__name__)
CORS(app)

# Add a simple root route for testing
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'success': True,
        'message': 'Test server is running',
        'timestamp': '2025-04-16'
    })

# Try to add the current directory to the Python path
sys.path.insert(0, os.getcwd())
print("Python path:", sys.path)

# Import the TradingView blueprint
try:
    from api.routes.tradingview_integration import tradingview_bp
    print("Successfully imported TradingView blueprint from api.routes")
except ImportError as e1:
    print(f"Import error from api.routes: {e1}")
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'api'))
        print("Added api directory to Python path")
        
        from routes.tradingview_integration import tradingview_bp
        print("Successfully imported TradingView blueprint from routes")
    except ImportError as e2:
        print(f"Import error from routes: {e2}")
        
        # Try one more approach - check if the file exists directly
        tradingview_file = os.path.join(os.getcwd(), 'api', 'routes', 'tradingview_integration.py')
        print(f"Checking if file exists at {tradingview_file}: {os.path.exists(tradingview_file)}")
        
        # Exit with error
        print("Could not import TradingView blueprint from either location")
        print("Will run with just the root route for testing")

# Register the blueprint if available
try:
    if 'tradingview_bp' in locals():
        app.register_blueprint(tradingview_bp)
        print("Registered TradingView blueprint")
    else:
        print("WARNING: No blueprint to register")
except Exception as e:
    print(f"Error registering blueprint: {e}")

# Print all available routes
print("\nAvailable routes:")
for rule in app.url_map.iter_rules():
    print(f"Route: {rule.endpoint} -> {rule.rule}")

# Run the Flask app
if __name__ == '__main__':
    try:
        port = 5001  # Use a different port to avoid conflicts
        print(f"\nStarting test server on port {port}...")
        print(f"Root route: http://localhost:{port}/")
        print(f"Test route: http://localhost:{port}/api/tradingview/test (if blueprint registered)")
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc() 