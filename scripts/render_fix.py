#!/usr/bin/env python
"""
Render Deployment Fix Script

This script contains functions to fix common issues with Render deployment,
primarily related to frontend file serving and configuration.
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
    """Ensure a directory exists"""
    try:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {e}")
        return False

def copy_file(source, destination):
    """Copy a file from source to destination"""
    try:
        if os.path.exists(source):
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copy2(source, destination)
            logger.info(f"Copied {source} to {destination}")
            return True
        else:
            logger.warning(f"Source file does not exist: {source}")
            return False
    except Exception as e:
        logger.error(f"Failed to copy {source} to {destination}: {e}")
        return False

def write_file(path, content):
    """Write content to a file"""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        logger.info(f"Wrote content to {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to write to {path}: {e}")
        return False

def create_fallback_index_html(directory):
    """Create a fallback index.html file"""
    try:
        index_path = os.path.join(directory, 'index.html')
        if os.path.exists(index_path):
            logger.info(f"index.html already exists at {index_path}")
            return True
            
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Trading Bot</title>
    <link rel="stylesheet" href="/static/css/main.css">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 800px;
            padding: 2rem;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            margin: 2rem;
        }
        h1 {
            color: #0366d6;
            margin-bottom: 1rem;
        }
        .logo {
            max-width: 120px;
            margin-bottom: 1.5rem;
        }
        .header {
            margin-bottom: 2rem;
        }
        .status {
            display: inline-block;
            padding: 0.5rem 1rem;
            background-color: #e1f5fe;
            color: #0366d6;
            border-radius: 4px;
            font-weight: bold;
            margin: 1rem 0;
        }
        .button {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background-color: #0366d6;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            margin-top: 1rem;
            transition: background-color 0.2s;
        }
        .button:hover {
            background-color: #0056b3;
        }
        p {
            line-height: 1.6;
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Trading Bot</h1>
            <div class="status">API Status: Running</div>
        </div>
        <div>
            <p>The API server is operational and ready to process requests.</p>
            <p>This is a fallback page created by the render_fix script.</p>
            <a href="/api/test" class="button">Test API Connection</a>
        </div>
    </div>
    <script src="/static/js/main.js"></script>
</body>
</html>
        """
        
        with open(index_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Created fallback index.html at {index_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create fallback index.html: {e}")
        return False

def create_basic_css_file(directory):
    """Create a basic CSS file if none exists"""
    try:
        css_dir = os.path.join(directory, 'css')
        os.makedirs(css_dir, exist_ok=True)
        
        css_path = os.path.join(css_dir, 'main.css')
        if os.path.exists(css_path):
            logger.info(f"CSS file already exists at {css_path}")
            return True
            
        css_content = """
/* Basic CSS styles */
:root {
    --primary-color: #0366d6;
    --secondary-color: #f5f5f5;
    --text-color: #333;
    --accent-color: #e1f5fe;
    --border-color: #e1e4e8;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: var(--secondary-color);
    color: var(--text-color);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
}

header {
    background-color: var(--primary-color);
    color: white;
    padding: 1rem;
}

main {
    padding: 1rem;
}

footer {
    padding: 1rem;
    background-color: var(--secondary-color);
    border-top: 1px solid var(--border-color);
    text-align: center;
    font-size: 0.875rem;
    color: #666;
}

.card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.button {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background-color: var(--primary-color);
    color: white;
    text-decoration: none;
    border-radius: 4px;
    font-weight: bold;
    border: none;
    cursor: pointer;
}

.button:hover {
    opacity: 0.9;
}
        """
        
        with open(css_path, 'w') as f:
            f.write(css_content)
        
        logger.info(f"Created basic CSS file at {css_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create basic CSS file: {e}")
        return False

def create_basic_js_file(directory):
    """Create a basic JavaScript file if none exists"""
    try:
        js_dir = os.path.join(directory, 'js')
        os.makedirs(js_dir, exist_ok=True)
        
        js_path = os.path.join(js_dir, 'main.js')
        if os.path.exists(js_path):
            logger.info(f"JavaScript file already exists at {js_path}")
            return True
            
        js_content = """
// Basic JavaScript for frontend functionality

document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Trading Bot frontend loaded');
    
    // Check API connection
    const apiStatusElement = document.querySelector('.status');
    if (apiStatusElement) {
        fetch('/api/test')
            .then(response => response.json())
            .then(data => {
                if (data && data.success) {
                    apiStatusElement.textContent = `API Status: Connected (${data.version || 'Unknown'})`;
                    apiStatusElement.style.backgroundColor = '#e6ffed';
                    apiStatusElement.style.color = '#28a745';
                } else {
                    apiStatusElement.textContent = 'API Status: Error';
                    apiStatusElement.style.backgroundColor = '#ffeef0';
                    apiStatusElement.style.color = '#d73a49';
                }
            })
            .catch(error => {
                console.error('API connection error:', error);
                apiStatusElement.textContent = 'API Status: Connection Error';
                apiStatusElement.style.backgroundColor = '#ffeef0';
                apiStatusElement.style.color = '#d73a49';
            });
    }
});
        """
        
        with open(js_path, 'w') as f:
            f.write(js_content)
        
        logger.info(f"Created basic JS file at {js_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create basic JS file: {e}")
        return False

def ensure_frontend_directories():
    """Ensure frontend directories exist"""
    try:
        # Define all directories to create
        directories = [
            'frontend/build',
            'frontend/build/static',
            'frontend/build/static/css',
            'frontend/build/static/js',
            'frontend/build/static/images',
            'static',
            'static/css',
            'static/js',
            'static/images'
        ]
        
        # Create each directory
        for directory in directories:
            ensure_directory(directory)
        
        return True
    except Exception as e:
        logger.error(f"Error creating frontend directories: {e}")
        return False

def ensure_config_files():
    """Ensure all necessary config files exist"""
    try:
        # Base directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Config files to check and create if missing
        config_files = {
            'config.json': {
                'debug': True,
                'use_mock_data': True,
                'api_keys': {
                    'tradingview': '',
                    'alpaca': ''
                }
            },
            'broker_config.json': {
                'broker': 'alpaca',
                'paper_trading': True,
                'alpaca': {
                    'api_key': '',
                    'api_secret': ''
                }
            },
            'execution_model_config.json': {
                'model_type': 'rsi',
                'parameters': {
                    'rsi_threshold_low': 30,
                    'rsi_threshold_high': 70
                }
            },
            os.path.join('config', 'environments', 'market_data_config.json'): {
                'active_source': 'mock',
                'mock': {
                    'use_csv_data': True
                },
                'alpaca': {
                    'api_key': '',
                    'api_secret': ''
                }
            }
        }
        
        # Create config files if they don't exist
        for config_file, default_content in config_files.items():
            file_path = os.path.join(base_dir, config_file)
            
            # Make sure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump(default_content, f, indent=2)
                logger.info(f"Created config file: {file_path}")
            else:
                logger.info(f"Config file already exists: {file_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating config files: {e}")
        return False

def enhanced_copy_frontend_files():
    """
    Improved function to ensure frontend files are available in all necessary locations
    This handles both direct copying and symbolic linking with multiple fallbacks
    """
    logger.info("Running enhanced frontend file distribution")
    
    # Define all the key paths we need
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_dir = os.path.join(base_dir, 'frontend', 'build')
    static_dir = os.path.join(base_dir, 'static')
    backend_static_dir = os.path.join(base_dir, 'backend', 'static')
    
    # Ensure source directory exists
    if not os.path.exists(source_dir):
        logger.warning(f"Source frontend directory does not exist: {source_dir}")
        
        # Create source directory with minimal files
        ensure_directory(source_dir)
        ensure_directory(os.path.join(source_dir, 'static', 'css'))
        ensure_directory(os.path.join(source_dir, 'static', 'js'))
        
        # Create fallback files
        create_fallback_index_html(source_dir)
        create_basic_css_file(os.path.join(source_dir, 'static'))
        create_basic_js_file(os.path.join(source_dir, 'static'))
    
    # Ensure target directories exist
    ensure_directory(static_dir)
    ensure_directory(os.path.join(static_dir, 'css'))
    ensure_directory(os.path.join(static_dir, 'js'))
    ensure_directory(backend_static_dir)
    
    # Copy index.html to root directory
    source_index = os.path.join(source_dir, 'index.html')
    target_index = os.path.join(base_dir, 'index.html')
    if os.path.exists(source_index):
        shutil.copy2(source_index, target_index)
        logger.info(f"Copied {source_index} to {target_index}")
    else:
        # Create fallback index if source doesn't exist
        create_fallback_index_html(base_dir)
    
    # Copy source directory to static directory
    try:
        # Copy all files from frontend/build to static
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                source_file = os.path.join(root, file)
                relative_path = os.path.relpath(source_file, source_dir)
                target_file = os.path.join(static_dir, relative_path)
                
                # Make sure target directory exists
                os.makedirs(os.path.dirname(target_file), exist_ok=True)
                
                # Copy the file
                shutil.copy2(source_file, target_file)
        
        logger.info(f"Copied all files from {source_dir} to {static_dir}")
    except Exception as e:
        logger.error(f"Error copying files from {source_dir} to {static_dir}: {e}")
    
    # Copy specific static files to backend/static dir
    if os.path.exists(os.path.join(source_dir, 'static')):
        target_static = os.path.join(backend_static_dir)
        try:
            # Create backend/static/css and backend/static/js
            os.makedirs(os.path.join(target_static, 'css'), exist_ok=True)
            os.makedirs(os.path.join(target_static, 'js'), exist_ok=True)
            
            # Copy CSS files
            for file in os.listdir(os.path.join(source_dir, 'static', 'css')):
                source_file = os.path.join(source_dir, 'static', 'css', file)
                target_file = os.path.join(target_static, 'css', file)
                shutil.copy2(source_file, target_file)
            
            # Copy JS files
            for file in os.listdir(os.path.join(source_dir, 'static', 'js')):
                source_file = os.path.join(source_dir, 'static', 'js', file)
                target_file = os.path.join(target_static, 'js', file)
                shutil.copy2(source_file, target_file)
                
            logger.info(f"Copied static files to {target_static}")
        except Exception as e:
            logger.error(f"Error copying static files to backend/static: {e}")
            
            # Create fallback files in backend/static
            create_basic_css_file(target_static)
            create_basic_js_file(target_static)
    
    return True

def run_render_fix():
    """Main function to run all render fixes"""
    logger.info("Starting render fix process")
    
    # Ensure all necessary directories exist
    ensure_frontend_directories()
    
    # Make sure config files exist
    ensure_config_files()
    
    # Copy frontend files to static folder
    enhanced_copy_frontend_files()
    
    logger.info("Render fix process completed")
    return True

if __name__ == '__main__':
    run_render_fix() 