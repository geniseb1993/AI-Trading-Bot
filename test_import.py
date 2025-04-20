import os
import sys
import traceback

# Add the current directory to the path
print("Current directory:", os.getcwd())
sys.path.insert(0, os.getcwd())

# Print Python path
print("\nPython path:")
for p in sys.path:
    print(f"  - {p}")

# Try different import variations
tests = [
    "from api.routes.ceo_dashboard_routes import ceo_dashboard_bp",
    "from routes.ceo_dashboard_routes import ceo_dashboard_bp",
    "import api.routes.ceo_dashboard_routes",
    "import api",
    "import api.routes",
    "from api import routes"
]

print("\nImport tests:")
for test in tests:
    try:
        print(f"\nTrying: {test}")
        exec(test)
        print(f"Success: {test}")
    except Exception as e:
        print(f"Failed: {test}")
        print(f"Error: {e}")
        # Print traceback for debugging
        traceback.print_exc()

# Check if specific files exist
api_init = os.path.join(os.getcwd(), "api", "__init__.py")
routes_init = os.path.join(os.getcwd(), "api", "routes", "__init__.py")
utils_init = os.path.join(os.getcwd(), "api", "utils", "__init__.py")
target_file = os.path.join(os.getcwd(), "api", "routes", "ceo_dashboard_routes.py")

print("\nChecking files:")
print(f"api/__init__.py exists: {os.path.exists(api_init)}")
print(f"api/routes/__init__.py exists: {os.path.exists(routes_init)}")
print(f"api/utils/__init__.py exists: {os.path.exists(utils_init)}")
print(f"api/routes/ceo_dashboard_routes.py exists: {os.path.exists(target_file)}")

print("\nDone") 