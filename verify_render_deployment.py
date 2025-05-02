#!/usr/bin/env python
"""
Verify Render Deployment

This script checks that all necessary files and modules are available
for the AI Trading Bot application running on Render.
"""

import os
import sys
import json
import importlib
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('verify_deployment')

def check_file_exists(filepath, create_empty=False, default_content=None):
    """
    Check if a file exists, optionally creating it if missing.
    
    Args:
        filepath (str): Path to the file to check
        create_empty (bool): Whether to create an empty file if it doesn't exist
        default_content (dict, optional): Default content for the file if created
        
    Returns:
        bool: True if the file exists or was created, False otherwise
    """
    if os.path.exists(filepath):
        logger.info(f"✓ File exists: {filepath}")
        return True
    else:
        logger.warning(f"✗ File missing: {filepath}")
        if create_empty:
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # Create the file
                if default_content is not None and isinstance(default_content, dict):
                    with open(filepath, 'w') as f:
                        json.dump(default_content, f, indent=2)
                else:
                    with open(filepath, 'w') as f:
                        f.write('{}')
                logger.info(f"  Created file: {filepath}")
                return True
            except Exception as e:
                logger.error(f"  Failed to create file: {e}")
                return False
        return False

def check_module_imports(modules):
    """
    Check if modules can be imported.
    
    Args:
        modules (list): List of module names to check
        
    Returns:
        tuple: (success_count, total_count)
    """
    success_count = 0
    for module_name in modules:
        try:
            # Try to import the module
            module = importlib.import_module(module_name)
            logger.info(f"✓ Module available: {module_name}")
            success_count += 1
        except ImportError as e:
            logger.warning(f"✗ Module missing: {module_name} ({e})")
            # If it's alpaca_trade_api, check mock_modules
            if module_name == 'alpaca_trade_api':
                try:
                    mock_dir = os.path.join(os.path.dirname(__file__), 'mock_modules')
                    if mock_dir not in sys.path:
                        sys.path.insert(0, mock_dir)
                    module = importlib.import_module(module_name)
                    logger.info(f"✓ Mock module available: {module_name}")
                    success_count += 1
                except ImportError as mock_e:
                    logger.warning(f"✗ Mock module also missing: {module_name} ({mock_e})")
    
    return success_count, len(modules)

def check_directories():
    """
    Check that all required directories exist, creating them if necessary.
    
    Returns:
        tuple: (success_count, total_count)
    """
    # List of required directories
    required_dirs = [
        'data',
        'data/logs',
        'data/broker',
        'data/market_data',
        'static',
        'static/css',
        'static/js',
        'config',
        'config/environments',
        'mock_modules'
    ]
    
    success_count = 0
    for directory in required_dirs:
        if os.path.exists(directory):
            logger.info(f"✓ Directory exists: {directory}")
            success_count += 1
        else:
            logger.warning(f"✗ Directory missing: {directory}")
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"  Created directory: {directory}")
                success_count += 1
            except Exception as e:
                logger.error(f"  Failed to create directory: {e}")
    
    return success_count, len(required_dirs)

def check_config_files():
    """
    Check that all required configuration files exist.
    
    Returns:
        tuple: (success_count, total_count)
    """
    # List of required configuration files with default content
    config_files = {
        'config.json': {
            "app": {
                "name": "AI Trading Bot",
                "version": "2.0.0",
                "environment": "production",
                "debug": False
            }
        },
        'broker_config.json': {
            "active_broker": "mock",
            "brokers": {
                "mock": {
                    "enabled": True
                }
            }
        },
        'execution_model_config.json': {
            "execution": {
                "mode": "simulated",
                "dry_run": True
            }
        },
        'config/environments/market_data_config.json': {
            "active_source": "mock",
            "use_real_data": False,
            "sources": {
                "mock": {
                    "enabled": True
                }
            }
        }
    }
    
    success_count = 0
    for filepath, default_content in config_files.items():
        if check_file_exists(filepath, create_empty=True, default_content=default_content):
            success_count += 1
    
    return success_count, len(config_files)

def check_render_environment():
    """
    Check if we're running on Render and verify environment variables.
    
    Returns:
        bool: True if environment looks good, False otherwise
    """
    is_render = os.environ.get('RENDER', '').lower() == 'true'
    logger.info(f"Running on Render: {is_render}")
    
    # Get PORT environment variable
    port = os.environ.get('PORT')
    if port:
        logger.info(f"PORT environment variable: {port}")
        try:
            port_int = int(port)
            logger.info(f"PORT value is valid integer: {port_int}")
        except ValueError:
            logger.warning(f"PORT value is not a valid integer: {port}")
    else:
        logger.warning("PORT environment variable not set")
    
    # Check other environment variables
    env_vars = [
        'PYTHON_VERSION',
        'FLASK_ENV',
        'FLASK_APP',
        'STATIC_FOLDER',
        'RENDER_DEPLOYMENT'
    ]
    
    env_count = 0
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            logger.info(f"✓ Environment variable set: {var}={value}")
            env_count += 1
        else:
            logger.warning(f"✗ Environment variable not set: {var}")
    
    return env_count == len(env_vars)

def main():
    """Main verification function"""
    logger.info("Starting Render deployment verification")
    
    # Check environment
    env_ok = check_render_environment()
    
    # Check directories
    dir_count, dir_total = check_directories()
    logger.info(f"Directories: {dir_count}/{dir_total} verified")
    
    # Check config files
    config_count, config_total = check_config_files()
    logger.info(f"Config files: {config_count}/{config_total} verified")
    
    # Check required module imports
    modules = [
        'flask',
        'flask_cors',
        'pandas',
        'numpy',
        'alpaca_trade_api'
    ]
    module_count, module_total = check_module_imports(modules)
    logger.info(f"Module imports: {module_count}/{module_total} verified")
    
    # Check port handling in wsgi.py
    wsgi_fixed = False
    try:
        import wsgi
        wsgi_fixed = hasattr(wsgi, 'get_port') or hasattr(wsgi, 'app')
        if wsgi_fixed:
            logger.info("✓ wsgi.py has proper port handling")
        else:
            logger.warning("✗ wsgi.py may not have proper port handling")
    except ImportError:
        logger.warning("✗ Could not import wsgi module")
    
    # Check the route registrations in app
    try:
        from api.app import app
        route_count = len(app.url_map._rules)
        logger.info(f"Flask app has {route_count} routes registered")
    except ImportError:
        try:
            from app import app
            route_count = len(app.url_map._rules)
            logger.info(f"Flask app has {route_count} routes registered")
        except ImportError:
            logger.warning("✗ Could not import Flask app")
    
    # Summary
    total_score = (
        dir_count / dir_total +
        config_count / config_total +
        module_count / module_total +
        (1 if wsgi_fixed else 0) +
        (1 if env_ok else 0)
    ) / 5 * 100
    
    logger.info(f"Deployment verification complete: {total_score:.1f}% ready")
    
    # Print overall result
    if total_score >= 80:
        logger.info("✅ Deployment appears ready")
        return 0
    else:
        logger.warning("⚠️ Deployment has some issues that need to be addressed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 