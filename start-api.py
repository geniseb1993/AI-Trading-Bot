import os
import sys
import subprocess
import importlib.util

# Check required packages
required_packages = ['flask', 'flask_cors', 'pandas', 'plyer', 'pyttsx3']
missing_packages = []

for package in required_packages:
    if not importlib.util.find_spec(package):
        missing_packages.append(package)

if missing_packages:
    print(f"Installing missing packages: {', '.join(missing_packages)}")
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
    print("Required packages installed successfully.")

# Run the Flask app
print("Starting Flask API server...")
api_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api')
app_path = os.path.join(api_dir, 'app.py')

if not os.path.exists(app_path):
    print(f"Error: {app_path} not found!")
    sys.exit(1)

# Change to the api directory
os.chdir(api_dir)
print(f"Changed directory to: {os.getcwd()}")

# Make sure both root and api directories are in the Python path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)
sys.path.insert(0, api_dir)
# Add execution_model to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'execution_model'))

# Add api/lib to Python path explicitly
lib_dir = os.path.join(api_dir, 'lib')
if os.path.exists(lib_dir):
    sys.path.insert(0, lib_dir)
    print(f"Added {lib_dir} to Python path")

# Print the Python path for debugging
print("Python path:")
for path in sys.path:
    print(f" - {path}")

# Run the Flask app directly instead of importing it
try:
    print(f"Running Flask app: {app_path}")
    # Use subprocess to run the app.py directly
    result = subprocess.run([sys.executable, app_path], 
                          cwd=api_dir,
                          env=os.environ.copy())
    if result.returncode != 0:
        print(f"Flask app exited with error code: {result.returncode}")
        sys.exit(result.returncode)
except Exception as e:
    print(f"Error starting Flask app: {str(e)}")
    sys.exit(1) 