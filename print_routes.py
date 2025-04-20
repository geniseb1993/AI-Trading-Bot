import sys
import os

# Add the current directory to the Python path
sys.path.append(os.getcwd())

# Try to import the Flask app
try:
    from api.app import app
    
    print("\n===== REGISTERED ROUTES =====")
    for rule in app.url_map.iter_rules():
        print(f"Route: {rule.endpoint} -> {rule.rule}")
    print("============================\n")
except Exception as e:
    print(f"Error importing Flask app: {e}") 