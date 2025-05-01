#!/usr/bin/env python3
"""
Check Requirements

This script checks for required packages and handles optional dependencies
by creating mock modules when dependencies cannot be installed.
"""

import os
import sys
import logging
import importlib.util
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('check_requirements')

# Define core packages that are always required
CORE_PACKAGES = [
    'flask',
    'flask-cors',
    'python-dotenv',
    'requests',
    'pandas',
    'numpy',
    'gunicorn',
]

# Define optional packages that can be mocked if not available
OPTIONAL_PACKAGES = [
    'polygon-api-client',
    'alpaca-trade-api',
    'plyer',
    'pygame',
    'pyttsx3',
    'openai',
]

def is_package_installed(package_name):
    """Check if a package is installed"""
    normalized_name = package_name.lower().replace('-', '_')
    try:
        importlib.import_module(normalized_name)
        return True
    except ImportError:
        # Try alternate import names
        alt_names = []
        if '-' in package_name:
            alt_names.append(package_name.replace('-', '_'))
        elif '_' in package_name:
            alt_names.append(package_name.replace('_', '-'))
            
        # Special cases
        if package_name == 'polygon-api-client':
            alt_names.append('polygon')
        elif package_name == 'alpaca-trade-api':
            alt_names.append('alpaca_trade_api')
        elif package_name == 'flask-cors':
            alt_names.append('flask_cors')
            
        for name in alt_names:
            try:
                importlib.import_module(name)
                return True
            except ImportError:
                continue
                
        return False

def install_package(package_name):
    """Attempt to install a package using pip"""
    try:
        logger.info(f"Attempting to install {package_name}")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
        return True
    except subprocess.CalledProcessError:
        logger.error(f"Failed to install {package_name}")
        return False

def ensure_mock_module(package_name):
    """Ensure a mock module exists for the package"""
    mock_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_modules')
    os.makedirs(mock_dir, exist_ok=True)
    
    # Convert package name to module name
    module_name = package_name.lower().replace('-', '_')
    if package_name == 'polygon-api-client':
        module_name = 'polygon'
    elif package_name == 'alpaca-trade-api':
        module_name = 'alpaca_trade_api'
    
    mock_file = os.path.join(mock_dir, f"{module_name}.py")
    
    # Only create the mock file if it doesn't exist
    if not os.path.exists(mock_file):
        logger.info(f"Creating mock module for {package_name} at {mock_file}")
        with open(mock_file, 'w') as f:
            f.write(f'''"""
Mock implementation of the {package_name} module.

This is a placeholder that provides minimal functionality.
"""

# Define a placeholder class that logs when methods are called
class _MockClass:
    def __init__(self, *args, **kwargs):
        import logging
        self.logger = logging.getLogger('{package_name}')
        self.logger.warning(f"Using mock implementation of {package_name}")
        
    def __getattr__(self, name):
        def mock_method(*args, **kwargs):
            self.logger.warning(f"Called mock method {{name}} on {package_name}")
            return None
        return mock_method

# Export common names that might be imported
''')
            
            # Add package-specific mock implementations
            if module_name == 'polygon':
                f.write('''
class RESTClient(_MockClass):
    """Mock implementation of polygon.RESTClient"""
    pass
''')
            elif module_name == 'alpaca_trade_api':
                f.write('''
class REST(_MockClass):
    """Mock implementation of alpaca_trade_api.REST"""
    pass
''')
            elif module_name == 'plyer':
                f.write('''
# Create a notification singleton
class _NotificationMock:
    def notify(self, title='', message='', app_name='', app_icon='', timeout=10, ticker=''):
        import logging
        logging.info(f"MOCK NOTIFICATION: {title} - {message}")
        return True

notification = _NotificationMock()
''')
            elif module_name == 'pyttsx3':
                f.write('''
def init(*args, **kwargs):
    return _MockEngine()
    
class _MockEngine:
    def say(self, text):
        import logging
        logging.info(f"MOCK TTS: {text}")
        
    def runAndWait(self):
        pass
        
    def stop(self):
        pass
''')
    
    return mock_file

def check_and_install_packages():
    """Check and install packages, creating mocks for optional ones that fail"""
    missing_core = []
    mocked_packages = []
    
    # Check and install core packages
    for package in CORE_PACKAGES:
        if not is_package_installed(package):
            success = install_package(package)
            if not success:
                missing_core.append(package)
    
    # Check optional packages
    for package in OPTIONAL_PACKAGES:
        if not is_package_installed(package):
            success = install_package(package)
            if not success:
                mock_file = ensure_mock_module(package)
                mocked_packages.append(package)
    
    # Add mock_modules directory to sys.path if there are any mocked packages
    if mocked_packages:
        mock_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_modules')
        if mock_dir not in sys.path:
            sys.path.insert(0, mock_dir)
            logger.info(f"Added {mock_dir} to Python path")
    
    return missing_core, mocked_packages

if __name__ == "__main__":
    logger.info("Checking and installing required packages")
    missing_core, mocked_packages = check_and_install_packages()
    
    if missing_core:
        logger.error(f"Missing core packages: {', '.join(missing_core)}")
        logger.error("The application may not function correctly!")
    else:
        logger.info("All core packages are installed")
        
    if mocked_packages:
        logger.warning(f"Created mock modules for: {', '.join(mocked_packages)}")
        logger.warning("Some functionality may be limited")
        
    logger.info("Package check completed") 