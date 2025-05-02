#!/usr/bin/env python
"""
Verify Render Deployment

This script checks if all the fixes for Render deployment have been correctly applied.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_file_exists(path, required=True):
    """Check if a file exists and log the result."""
    if os.path.exists(path):
        logger.info(f"✅ Found {path}")
        return True
    else:
        if required:
            logger.error(f"❌ Missing required file: {path}")
        else:
            logger.warning(f"⚠️ Optional file not found: {path}")
        return False

def check_package_in_requirements(package_name):
    """Check if a package is in requirements.txt."""
    requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
    if not os.path.exists(requirements_path):
        logger.error(f"❌ Requirements file not found: {requirements_path}")
        return False
    
    with open(requirements_path, 'r') as f:
        content = f.read()
        if package_name in content:
            logger.info(f"✅ Package {package_name} found in requirements.txt")
            return True
        else:
            logger.error(f"❌ Package {package_name} not found in requirements.txt")
            return False

def check_config_files():
    """Check if required configuration files exist and have valid JSON content."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_files = [
        'config.json',
        'broker_config.json',
        'execution_model_config.json'
    ]
    
    all_valid = True
    for config_file in config_files:
        path = os.path.join(base_dir, config_file)
        if check_file_exists(path):
            # Check if it's valid JSON
            try:
                with open(path, 'r') as f:
                    json.load(f)
                logger.info(f"✅ {config_file} contains valid JSON")
            except json.JSONDecodeError:
                logger.error(f"❌ {config_file} contains invalid JSON")
                all_valid = False
        else:
            all_valid = False
    
    return all_valid

def check_static_files():
    """Check if required static files exist."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, 'static')
    css_dir = os.path.join(static_dir, 'css')
    js_dir = os.path.join(static_dir, 'js')
    
    all_valid = True
    # Check directories
    for directory in [static_dir, css_dir, js_dir]:
        if os.path.exists(directory) and os.path.isdir(directory):
            logger.info(f"✅ Directory exists: {directory}")
        else:
            logger.warning(f"⚠️ Directory missing: {directory}")
            os.makedirs(directory, exist_ok=True)
            logger.info(f"  Created directory: {directory}")
    
    # Check files
    index_html = os.path.join(static_dir, 'index.html')
    main_css = os.path.join(css_dir, 'main.css')
    
    if not check_file_exists(index_html):
        all_valid = False
        # Create a basic index.html
        try:
            with open(index_html, 'w') as f:
                f.write("""<!DOCTYPE html>
<html>
<head>
    <title>AI Trading Bot</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div style="max-width: 800px; margin: 100px auto; text-align: center;">
        <h1>AI Trading Bot</h1>
        <p>The API server is running successfully.</p>
    </div>
</body>
</html>""")
            logger.info(f"  Created basic index.html at {index_html}")
        except Exception as e:
            logger.error(f"  Failed to create index.html: {str(e)}")
    
    if not check_file_exists(main_css):
        all_valid = False
        # Create a basic CSS file
        try:
            with open(main_css, 'w') as f:
                f.write("""body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #121212;
    color: #e1e1e1;
}
h1 {
    color: #4a90e2;
}""")
            logger.info(f"  Created basic CSS file at {main_css}")
        except Exception as e:
            logger.error(f"  Failed to create CSS file: {str(e)}")
    
    return all_valid

def check_wsgi_file():
    """Check if the wsgi.py file has the fix for the 'int' object error."""
    wsgi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wsgi.py')
    if not check_file_exists(wsgi_path):
        return False
    
    with open(wsgi_path, 'r') as f:
        content = f.read()
        # Check for the fix or related code
        if "# Fix for the 'int' object has no attribute 'get' error" in content or "port = os.environ.get('PORT')" in content:
            logger.info("✅ wsgi.py contains fix for 'int' object error")
            return True
        else:
            logger.warning("⚠️ wsgi.py might not have the fix for 'int' object error")
            return False

def main():
    """Run all checks and report results."""
    logger.info("🔍 Verifying Render deployment fixes...")
    
    # Initialize counters
    checks_total = 0
    checks_passed = 0
    
    # Check packages in requirements.txt
    checks_total += 1
    if check_package_in_requirements('alpaca-trade-api'):
        checks_passed += 1
    
    # Check config files
    checks_total += 1
    if check_config_files():
        checks_passed += 1
    
    # Check static files
    checks_total += 1
    if check_static_files():
        checks_passed += 1
    
    # Check wsgi.py fix
    checks_total += 1
    if check_wsgi_file():
        checks_passed += 1
    
    # Report results
    if checks_passed == checks_total:
        logger.info(f"✅ All checks passed! ({checks_passed}/{checks_total})")
        logger.info("🚀 Your Render deployment should work correctly now!")
    else:
        logger.warning(f"⚠️ Some checks failed. ({checks_passed}/{checks_total} passed)")
        logger.info("📝 Review the log above to address any remaining issues.")
    
    return checks_passed == checks_total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 