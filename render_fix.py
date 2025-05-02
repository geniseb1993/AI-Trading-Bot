#!/usr/bin/env python3
"""
Render Fix Script

This script prepares the environment for deployment on Render.
It creates necessary directories and basic files to ensure the application can start.
"""

import os
import sys
import logging
import shutil
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('render_fix')

def ensure_directory(directory):
    """Ensure a directory exists, creating it if necessary"""
    if not os.path.exists(directory):
        logger.info(f"Creating directory: {directory}")
        os.makedirs(directory, exist_ok=True)
    return directory

def copy_file(source, destination):
    """Copy a file if source exists"""
    if os.path.exists(source):
        logger.info(f"Copying {source} to {destination}")
        shutil.copy2(source, destination)
        return True
    return False

def write_file(path, content):
    """Write content to a file"""
    logger.info(f"Writing to {path}")
    with open(path, 'w') as f:
        f.write(content)

def create_fallback_index_html(directory):
    """Create a fallback index.html file in the specified directory"""
    file_path = os.path.join(directory, 'index.html')
    if not os.path.exists(file_path):
        logger.info(f"Creating fallback index.html at {file_path}")
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Trading Bot</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #121212;
            color: #e1e1e1;
        }
        .container {
            max-width: 800px;
            width: 90%;
            padding: 2rem;
            background-color: #1e1e1e;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        h1 {
            color: #4a90e2;
            margin-bottom: 1rem;
        }
        p {
            line-height: 1.6;
            margin-bottom: 1.5rem;
        }
        .status {
            padding: 0.5rem 1rem;
            background-color: #e7f3ff;
            border-radius: 4px;
            display: inline-block;
            font-weight: bold;
            color: #0062cc;
            margin-bottom: 1rem;
        }
        .api-link {
            display: inline-block;
            margin-top: 1rem;
            padding: 0.5rem 1rem;
            background-color: #4a90e2;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
        }
        .api-link:hover {
            background-color: #3a80d2;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
            text-align: left;
        }
        .card {
            background-color: #2d2d2d;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Trading Bot</h1>
        <div class="status">Server Status: Online</div>
        <p>The AI Trading Bot API is running and ready to process requests.</p>
        <div class="dashboard">
            <div class="card">
                <h3>API Status</h3>
                <p>The server is operational and handling requests.</p>
                <a href="/api/status" class="api-link">Check API Status</a>
            </div>
            <div class="card">
                <h3>Trading Status</h3>
                <p>Paper trading mode is active.</p>
                <p>Using mock broker implementation.</p>
            </div>
        </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            console.log('AI Trading Bot frontend initialized');
            
            // Check API status
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    console.log('API Status:', data);
                    const statusElement = document.querySelector('.status');
                    if (statusElement) {
                        statusElement.textContent = `Server Status: ${data.status || 'Online'}`;
                    }
                })
                .catch(error => {
                    console.error('Error checking API status:', error);
                    const statusElement = document.querySelector('.status');
                    if (statusElement) {
                        statusElement.textContent = 'Server Status: Error';
                        statusElement.style.backgroundColor = '#ffe0e0';
                        statusElement.style.color = '#d32f2f';
                    }
                });
        });
    </script>
</body>
</html>"""
        write_file(file_path, html_content)
        return file_path
    return None

def create_basic_css_file(directory):
    """Create a basic CSS file in the specified directory"""
    css_dir = os.path.join(directory, 'static', 'css')
    ensure_directory(css_dir)
    
    css_file = os.path.join(css_dir, 'main.css')
    if not os.path.exists(css_file):
        logger.info(f"Creating basic CSS file at {css_file}")
        css_content = """/* Basic styles for AI Trading Bot */
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #121212;
    color: #e1e1e1;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.card {
    background-color: #2d2d2d;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    padding: 20px;
    margin-bottom: 20px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px;
    background-color: #1e1e1e;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 4px;
    background-color: #4a90e2;
    color: white;
    text-decoration: none;
    font-weight: bold;
    border: none;
    cursor: pointer;
}

.btn:hover {
    background-color: #3a80d2;
}

.dashboard {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}
"""
        write_file(css_file, css_content)
        return css_file
    return None

def create_basic_js_file(directory):
    """Create a basic JavaScript file in the specified directory"""
    js_dir = os.path.join(directory, 'static', 'js')
    ensure_directory(js_dir)
    
    js_file = os.path.join(js_dir, 'main.js')
    if not os.path.exists(js_file):
        logger.info(f"Creating basic JS file at {js_file}")
        js_content = """// Basic JavaScript for AI Trading Bot
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Trading Bot frontend initialized');
    
    // Check API status
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            console.log('API Status:', data);
            const statusElement = document.querySelector('.status');
            if (statusElement) {
                statusElement.textContent = `Server Status: ${data.status || 'Online'}`;
            }
        })
        .catch(error => {
            console.error('Error checking API status:', error);
            const statusElement = document.querySelector('.status');
            if (statusElement) {
                statusElement.textContent = 'Server Status: Error';
                statusElement.style.backgroundColor = '#ffe0e0';
                statusElement.style.color = '#d32f2f';
            }
        });
});
"""
        write_file(js_file, js_content)
        return js_file
    return None

def ensure_frontend_directories():
    """Ensure all required frontend directories exist"""
    frontend_dirs = [
        'frontend/build',
        'frontend/build/static',
        'frontend/build/static/css',
        'frontend/build/static/js',
        'frontend/build/static/images',
        'static',
        'static/css',
        'static/js',
        'static/images',
    ]
    
    for directory in frontend_dirs:
        ensure_directory(directory)

def create_minimal_app_if_missing():
    """Create a minimal app.py file if it doesn't exist"""
    if not os.path.exists('app.py'):
        logger.info("Creating minimal app.py")
        app_content = """#!/usr/bin/env python3
from flask import Flask, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, static_folder='frontend/build')
CORS(app)

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'running',
        'mode': 'minimal',
        'message': 'Minimal Flask app is running'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

# Serve React app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
        
    # Check if we have an index.html file
    index_path = os.path.join(app.static_folder, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(app.static_folder, 'index.html')
        
    # Fallback to a simple HTML page
    return render_template_string('''
    <!DOCTYPE html>
    <html>
        <head>
            <title>AI Trading Bot</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background-color: #121212;
                    color: #e1e1e1;
                }
                .container {
                    max-width: 800px;
                    padding: 2rem;
                    background-color: #1e1e1e;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    text-align: center;
                }
                h1 {
                    color: #4a90e2;
                    margin-bottom: 1rem;
                }
                p {
                    line-height: 1.6;
                    margin-bottom: 1.5rem;
                }
                .status {
                    padding: 0.5rem 1rem;
                    background-color: #e7f3ff;
                    border-radius: 4px;
                    display: inline-block;
                    font-weight: bold;
                    color: #0062cc;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>AI Trading Bot</h1>
                <div class="status">API Status: Running</div>
                <p>The API server is operational and ready to process requests.</p>
            </div>
        </body>
    </html>
    ''')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
"""
        write_file('app.py', app_content)

def create_mock_directory():
    """Create the mock_modules directory if it doesn't exist"""
    mock_dir = ensure_directory('mock_modules')
    
    # Create __init__.py to make it a proper package
    init_file = os.path.join(mock_dir, '__init__.py')
    if not os.path.exists(init_file):
        logger.info(f"Creating {init_file}")
        write_file(init_file, '# Mock modules package\n')
    
    return mock_dir

def fix_execution_model():
    """Create a basic execution model module if it's missing"""
    exec_model_dir = ensure_directory('execution_model')
    
    # Create __init__.py
    init_file = os.path.join(exec_model_dir, '__init__.py')
    if not os.path.exists(init_file):
        logger.info(f"Creating {init_file}")
        write_file(init_file, '# Execution model package\n')
    
    return exec_model_dir

def ensure_frontend_serving_files():
    """Ensure all necessary files are in place for serving the frontend"""
    # Copy index.html to root directory
    root_index = 'index.html'
    frontend_index = os.path.join('frontend', 'build', 'index.html')
    
    if os.path.exists(frontend_index) and not os.path.exists(root_index):
        copy_file(frontend_index, root_index)
    
    # Copy CSS and JS files
    css_source = os.path.join('frontend', 'build', 'static', 'css', 'main.css')
    css_dest = os.path.join('static', 'css', 'main.css')
    
    js_source = os.path.join('frontend', 'build', 'static', 'js', 'main.js')
    js_dest = os.path.join('static', 'js', 'main.js')
    
    if os.path.exists(css_source) and not os.path.exists(css_dest):
        copy_file(css_source, css_dest)
    
    if os.path.exists(js_source) and not os.path.exists(js_dest):
        copy_file(js_source, js_dest)

def test_frontend_serving():
    """Test if the frontend serving works by checking for index.html"""
    frontend_index = os.path.join('frontend', 'build', 'index.html')
    if not os.path.exists(frontend_index):
        logger.warning("Frontend index.html not found, creating fallback")
        create_fallback_index_html('frontend/build')
        create_basic_css_file('frontend/build')
        create_basic_js_file('frontend/build')
        ensure_frontend_serving_files()
        return False
    return True

def copy_frontend_files(source_dir='frontend/build', dest_dir='static'):
    """Copy frontend files from source to destination if needed"""
    logger.info(f"Checking if frontend files need to be copied from {source_dir} to {dest_dir}")
    
    if not os.path.exists(source_dir):
        logger.warning(f"Source directory {source_dir} does not exist")
        return False
        
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
        
    # Check if index.html exists in source
    index_path = os.path.join(source_dir, 'index.html')
    if not os.path.exists(index_path):
        logger.warning(f"No index.html found in {source_dir}")
        return False
        
    # Copy index.html to destination
    dest_index = os.path.join(dest_dir, 'index.html')
    if not os.path.exists(dest_index):
        logger.info(f"Copying index.html to {dest_index}")
        shutil.copy2(index_path, dest_index)
        
    # Copy static files (CSS, JS, images)
    for subdir in ['css', 'js', 'images']:
        src_subdir = os.path.join(source_dir, 'static', subdir)
        dest_subdir = os.path.join(dest_dir, subdir)
        
        if os.path.exists(src_subdir):
            os.makedirs(dest_subdir, exist_ok=True)
            
            for file in os.listdir(src_subdir):
                src_file = os.path.join(src_subdir, file)
                dest_file = os.path.join(dest_subdir, file)
                
                if not os.path.exists(dest_file):
                    logger.info(f"Copying {src_file} to {dest_file}")
                    shutil.copy2(src_file, dest_file)
    
    return True

def create_symbolic_link(source, target):
    """Create a symbolic link from source to target if possible"""
    try:
        if os.path.exists(target):
            logger.info(f"Target {target} already exists, removing")
            if os.path.islink(target) or os.path.isfile(target):
                os.unlink(target)
            elif os.path.isdir(target):
                shutil.rmtree(target)
                
        logger.info(f"Creating symbolic link from {source} to {target}")
        os.symlink(source, target, target_is_directory=os.path.isdir(source))
        return True
    except Exception as e:
        logger.error(f"Error creating symbolic link: {e}")
        # Fall back to copying
        try:
            if os.path.isdir(source):
                if os.path.exists(target):
                    shutil.rmtree(target)
                shutil.copytree(source, target)
            else:
                if os.path.exists(target):
                    os.remove(target)
                shutil.copy2(source, target)
            logger.info(f"Copied {source} to {target} (symbolic link failed)")
            return True
        except Exception as copy_err:
            logger.error(f"Error copying instead of symlinking: {copy_err}")
            return False

def ensure_config_files():
    """Ensure all necessary configuration files exist"""
    # Define config files and their default content
    config_files = {
        'config.json': {
            "version": "1.0.0",
            "application_name": "AI Trading Bot",
            "environment": "production",
            "notifications": {
                "enabled": True,
                "email": False,
                "mobile": False,
                "desktop": True,
                "severity_level": "warning",
                "max_daily": 50
            },
            "market_data": {
                "default_provider": "mock",
                "use_cache": True,
                "cache_expiry": 3600
            },
            "execution": {
                "paper_trading": True,
                "max_positions": 10,
                "risk_level": "medium"
            },
            "ui": {
                "theme": "dark",
                "refresh_interval": 30
            }
        },
        'broker_config.json': {
            "default_broker": "mock",
            "brokers": {
                "mock": {
                    "enabled": True,
                    "paper_trading": True,
                    "initial_balance": 100000
                },
                "alpaca": {
                    "enabled": False,
                    "paper_trading": True,
                    "base_url": "https://paper-api.alpaca.markets",
                    "data_url": "https://data.alpaca.markets"
                }
            },
            "auto_trade": {
                "enabled": False,
                "max_positions": 5,
                "max_investment_per_trade": 10000,
                "stop_loss_percentage": 5,
                "take_profit_percentage": 10
            }
        },
        'execution_model_config.json': {
            "mode": "paper",
            "risk_level": "medium",
            "max_positions": 10,
            "position_sizing": "adaptive",
            "max_portfolio_risk_percent": 5,
            "max_position_risk_percent": 2,
            "stop_loss_percent": 3,
            "take_profit_percent": 5,
            "trailing_stop_enabled": True,
            "trailing_stop_percent": 1.5,
            "drawdown_protection": {
                "enabled": True,
                "max_daily_drawdown_percent": 5,
                "pause_trading_minutes": 120
            }
        },
        os.path.join('api', 'lib', 'market_data_config.json'): {
            "active_source": "mock",
            "use_real_data": False,
            "cache_enabled": True,
            "cache_expiry_seconds": 300,
            "sources": {
                "mock": {
                    "use_csv_data": True,
                    "data_directory": "data/market_data",
                    "volatility_factor": 1.0
                },
                "alpaca": {
                    "enabled": False,
                    "api_key": "",
                    "api_secret": "",
                    "paper_trading": True
                },
                "polygon": {
                    "enabled": False,
                    "api_key": ""
                }
            }
        }
    }
    
    # Ensure each config file exists
    for file_path, default_content in config_files.items():
        # Make sure directory exists
        dirname = os.path.dirname(file_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
            logger.info(f"Created directory {dirname}")
        
        # Create file if it doesn't exist
        if not os.path.exists(file_path):
            logger.info(f"Creating config file {file_path}")
            with open(file_path, 'w') as f:
                json.dump(default_content, f, indent=2)
        else:
            logger.info(f"Config file {file_path} already exists")

def copy_frontend_to_root():
    """Copy essential frontend files to the root directory for direct access"""
    # Find the frontend build directory
    frontend_build = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend', 'build')
    
    if not os.path.exists(frontend_build):
        logger.warning(f"Frontend build directory not found at {frontend_build}")
        return False
    
    # Copy index.html to root
    index_path = os.path.join(frontend_build, 'index.html')
    if os.path.exists(index_path):
        root_index = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
        logger.info(f"Copying {index_path} to {root_index}")
        shutil.copy2(index_path, root_index)
    
    # Create static directory in root if it doesn't exist
    static_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    if not os.path.exists(static_root):
        os.makedirs(static_root, exist_ok=True)
    
    # Copy static files
    static_src = os.path.join(frontend_build, 'static')
    if os.path.exists(static_src):
        for item in os.listdir(static_src):
            src_item = os.path.join(static_src, item)
            dest_item = os.path.join(static_root, item)
            
            if os.path.isdir(src_item):
                if not os.path.exists(dest_item):
                    os.makedirs(dest_item, exist_ok=True)
                
                # Copy files in the subdirectory
                for file in os.listdir(src_item):
                    src_file = os.path.join(src_item, file)
                    dest_file = os.path.join(dest_item, file)
                    
                    if os.path.isfile(src_file) and not os.path.exists(dest_file):
                        logger.info(f"Copying {src_file} to {dest_file}")
                        shutil.copy2(src_file, dest_file)
            elif os.path.isfile(src_item) and not os.path.exists(dest_item):
                logger.info(f"Copying {src_item} to {dest_item}")
                shutil.copy2(src_item, dest_item)
    
    return True

def enhanced_copy_frontend_files():
    """
    Improved function to ensure frontend files are available in all necessary locations
    This handles both direct copying and symbolic linking with multiple fallbacks
    """
    logger.info("Running enhanced frontend file distribution")
    
    # Define all the key paths we need
    source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend', 'build')
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure source directory exists
    if not os.path.exists(source_dir):
        logger.warning(f"Source frontend directory does not exist: {source_dir}")
        # Create minimal frontend files if source doesn't exist
        ensure_directory(source_dir)
        create_fallback_index_html(source_dir)
        create_basic_css_file(source_dir)
        create_basic_js_file(source_dir)
    
    # Ensure static directory exists
    ensure_directory(static_dir)
    
    # Create css/js/images subdirectories in static
    for subdir in ['css', 'js', 'images']:
        ensure_directory(os.path.join(static_dir, subdir))
    
    # First try: Copy index.html to root directory
    root_index = os.path.join(root_dir, 'index.html')
    frontend_index = os.path.join(source_dir, 'index.html')
    
    if os.path.exists(frontend_index):
        logger.info(f"Copying {frontend_index} to {root_index}")
        shutil.copy2(frontend_index, root_index)
    else:
        logger.warning(f"Frontend index.html not found at {frontend_index}")
    
    # Second: Copy all static files from frontend/build/static to static/
    frontend_static = os.path.join(source_dir, 'static')
    if os.path.exists(frontend_static):
        logger.info(f"Copying all static content from {frontend_static} to {static_dir}")
        
        # For each subdirectory (css, js, images)
        for subdir in os.listdir(frontend_static):
            src_subdir = os.path.join(frontend_static, subdir)
            dest_subdir = os.path.join(static_dir, subdir)
            
            # Skip if not a directory
            if not os.path.isdir(src_subdir):
                continue
                
            # Create destination subdirectory if it doesn't exist
            if not os.path.exists(dest_subdir):
                os.makedirs(dest_subdir, exist_ok=True)
            
            # Copy all files in the subdirectory
            for file in os.listdir(src_subdir):
                src_file = os.path.join(src_subdir, file)
                dest_file = os.path.join(dest_subdir, file)
                
                # Only copy files, not directories
                if os.path.isfile(src_file):
                    logger.info(f"Copying {src_file} to {dest_file}")
                    shutil.copy2(src_file, dest_file)
    else:
        logger.warning(f"Frontend static directory not found at {frontend_static}")
    
    # Third: Try to create symbolic links as an alternative approach
    try:
        # Link frontend/build/static to static in root
        if os.path.exists(frontend_static) and not os.path.exists(os.path.join(root_dir, 'static')):
            create_symbolic_link(frontend_static, os.path.join(root_dir, 'static'))
            logger.info(f"Created symbolic link from {frontend_static} to {os.path.join(root_dir, 'static')}")
    except Exception as e:
        logger.error(f"Error creating symbolic links: {e}")
    
    # Fourth: Copy any other necessary files from frontend/build to root
    for item in os.listdir(source_dir):
        src_item = os.path.join(source_dir, item)
        dest_item = os.path.join(root_dir, item)
        
        # Skip directories and certain files we don't need to copy
        if os.path.isdir(src_item) or item in ['index.html', 'static']:
            continue
            
        if os.path.isfile(src_item) and not os.path.exists(dest_item):
            logger.info(f"Copying additional file {src_item} to {dest_item}")
            shutil.copy2(src_item, dest_item)
    
    logger.info("Enhanced frontend file distribution completed")
    return True

def run_render_fix():
    """Main function to run all fixes"""
    logger.info("Starting render fix script")
    
    # Ensure directories
    ensure_frontend_directories()
    create_mock_directory()
    fix_execution_model()
    
    # Create fallback files
    create_fallback_index_html('frontend/build')
    create_fallback_index_html('.')
    create_basic_css_file('frontend/build')
    create_basic_js_file('frontend/build')
    
    # Create or copy JS and CSS files
    js_file = os.path.join('frontend', 'build', 'static', 'js', 'main.js')
    if not os.path.exists(js_file):
        create_basic_js_file('frontend/build')
    
    css_file = os.path.join('frontend', 'build', 'static', 'css', 'main.css')
    if not os.path.exists(css_file):
        create_basic_css_file('frontend/build')
    
    # Run enhanced frontend file distribution
    enhanced_copy_frontend_files()
    
    # Try copying frontend files to static folder
    copy_frontend_files('frontend/build', 'static')
    
    # Create minimal app if necessary
    create_minimal_app_if_missing()
    
    # Ensure config files exist
    ensure_config_files()
    
    logger.info("Render fix script completed successfully")
    return True

if __name__ == "__main__":
    run_render_fix()
