#!/usr/bin/env python
"""
Check Static Files

This script checks for all required static files and ensures they exist.
If files are missing, it tries to copy them from alternate locations.
"""

import os
import sys
import logging
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_static_files():
    """Check if all required static files exist."""
    # Get the project root directory
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Files to check
    files_to_check = [
        ('index.html', os.path.join(root_dir, 'index.html')),
        ('main.css', os.path.join(root_dir, 'static', 'css', 'main.css')),
        ('main.js', os.path.join(root_dir, 'static', 'js', 'main.js')),
        ('manifest.json', os.path.join(root_dir, 'static', 'manifest.json')),
        ('vicky.png', os.path.join(root_dir, 'static', 'images', 'vicky.png')),
        ('logo.png', os.path.join(root_dir, 'static', 'images', 'logo.png')),
        ('dashboard_ui.js', os.path.join(root_dir, 'static', 'js', 'dashboard_ui.js')),
    ]
    
    # Alternate locations to check
    alternate_locations = {
        'index.html': [
            os.path.join(root_dir, 'frontend', 'build', 'index.html'),
            os.path.join(root_dir, 'frontend', 'public', 'index.html'),
        ],
        'main.css': [
            os.path.join(root_dir, 'frontend', 'build', 'static', 'css', 'main.css'),
            os.path.join(root_dir, 'frontend', 'public', 'static', 'css', 'main.css'),
        ],
        'main.js': [
            os.path.join(root_dir, 'frontend', 'build', 'static', 'js', 'main.js'),
            os.path.join(root_dir, 'frontend', 'public', 'static', 'js', 'main.js'),
            os.path.join(root_dir, 'static', 'js', 'dashboard_ui.js'),  # Use dashboard_ui.js as fallback for main.js
        ],
        'manifest.json': [
            os.path.join(root_dir, 'frontend', 'build', 'manifest.json'),
            os.path.join(root_dir, 'frontend', 'public', 'manifest.json'),
        ],
        'vicky.png': [
            os.path.join(root_dir, 'frontend', 'build', 'static', 'images', 'vicky.png'),
            os.path.join(root_dir, 'frontend', 'public', 'images', 'vicky.png'),
        ],
        'logo.png': [
            os.path.join(root_dir, 'frontend', 'build', 'static', 'images', 'logo.png'),
            os.path.join(root_dir, 'static', 'images', 'vicky.png'),  # Use vicky.png as fallback for logo.png
            os.path.join(root_dir, 'frontend', 'public', 'images', 'vicky.png'),
        ],
        'dashboard_ui.js': [
            os.path.join(root_dir, 'frontend', 'build', 'static', 'js', 'dashboard_ui.js'),
            os.path.join(root_dir, 'static', 'js', 'main.js'),  # Use main.js as fallback for dashboard_ui.js
        ],
    }
    
    # Check and fix each file
    all_files_exist = True
    for file_name, file_path in files_to_check:
        if os.path.exists(file_path):
            logger.info(f"{file_name} exists at {file_path}")
        else:
            logger.warning(f"{file_name} is missing at {file_path}")
            all_files_exist = False
            
            # Try to copy from alternate locations
            if file_name in alternate_locations:
                for alt_path in alternate_locations[file_name]:
                    if os.path.exists(alt_path):
                        # Create the directory if it doesn't exist
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        
                        # Copy the file
                        try:
                            shutil.copy2(alt_path, file_path)
                            logger.info(f"Copied {file_name} from {alt_path} to {file_path}")
                            all_files_exist = True
                            break
                        except Exception as e:
                            logger.error(f"Error copying {file_name}: {e}")
            
            # If still missing and it's a critical file, create a default version
            if not os.path.exists(file_path):
                if file_name == 'index.html':
                    create_default_index_html(file_path)
                elif file_name == 'main.css':
                    create_default_main_css(file_path)
                elif file_name == 'main.js':
                    create_default_main_js(file_path)
                elif file_name == 'manifest.json':
                    create_default_manifest_json(file_path)
            
    return all_files_exist

def create_default_index_html(file_path):
    """Create a default index.html file."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#000000">
    <title>Vicki AI Trading Bot</title>
    
    <link rel="manifest" href="/static/manifest.json">
    <link rel="icon" href="/static/images/logo.png">
    <link rel="stylesheet" href="/static/css/main.css">
    
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #ffffff;
            margin: 0;
            padding: 0;
        }
        #root {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .app-loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            text-align: center;
        }
    </style>
</head>
<body>
    <div id="root">
        <div class="app-loading">
            <h2 style="color: #ff00ff;">VICKI AI Trading Bot</h2>
            <p>Loading application...</p>
        </div>
    </div>
    
    <script src="/static/js/main.js"></script>
</body>
</html>"""
    
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(html_content)
        logger.info(f"Created default index.html at {file_path}")
    except Exception as e:
        logger.error(f"Error creating default index.html: {e}")

def create_default_main_css(file_path):
    """Create a default main.css file."""
    css_content = """body {
    font-family: Arial, sans-serif;
    background-color: #121212;
    color: #ffffff;
    margin: 0;
    padding: 0;
}

#root {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.btn {
    display: inline-block;
    padding: 10px 20px;
    background-color: #ff00ff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    text-decoration: none;
}

.btn:hover {
    background-color: #cc00cc;
}"""
    
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(css_content)
        logger.info(f"Created default main.css at {file_path}")
    except Exception as e:
        logger.error(f"Error creating default main.css: {e}")

def create_default_main_js(file_path):
    """Create a default main.js file."""
    js_content = """/**
 * Main JavaScript for Vicki AI Trading Bot
 */
document.addEventListener('DOMContentLoaded', function() {
    const root = document.getElementById('root');
    if (!root) return;
    
    // Remove loading indicator if present
    const loader = root.querySelector('.app-loading');
    if (loader) {
        root.removeChild(loader);
    }
    
    // Create dashboard UI
    root.innerHTML = `
    <div style="display: flex; min-height: 100vh;">
        <!-- Sidebar -->
        <div style="width: 220px; background-color: #111; padding: 20px; border-right: 2px solid #ff00ff;">
            <div style="text-align: center; margin-bottom: 40px;">
                <img src="/static/images/logo.png" alt="Vicki Logo" style="width: 80px; height: 80px; border-radius: 50%;" 
                     onerror="this.onerror=null; this.src='/static/images/vicky.png';">
                <h2 style="color: #ff00ff; margin-top: 10px;">VICKY</h2>
            </div>
            
            <div style="margin-bottom: 30px;">
                <div style="display: flex; align-items: center; padding: 10px; background-color: #1e1e2f; margin-bottom: 10px; cursor: pointer; border-left: 4px solid #ff00ff; color: white;">
                    <span style="margin-right: 10px;">📊</span>
                    <span>Dashboard</span>
                </div>
                <div style="display: flex; align-items: center; padding: 10px; margin-bottom: 10px; cursor: pointer; color: #aaa;">
                    <span style="margin-right: 10px;">📈</span>
                    <span>Live Market</span>
                </div>
                <div style="display: flex; align-items: center; padding: 10px; margin-bottom: 10px; cursor: pointer; color: #aaa;">
                    <span style="margin-right: 10px;">🔍</span>
                    <span>Signals</span>
                </div>
            </div>
        </div>
        
        <!-- Main Content -->
        <div style="flex: 1; padding: 20px;">
            <div style="background-color: #1c1c2e; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
                <h2 style="color: #ddd; margin-top: 0;">Welcome to Vicki AI Trading Bot</h2>
                <p>Your AI-powered trading assistant is ready to help.</p>
                <div style="margin-top: 20px;">
                    <a href="/api/health" style="display: inline-block; background-color: #ff00ff; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; margin-right: 10px;">Check API Health</a>
                    <a href="/api/bot/status" style="display: inline-block; background-color: transparent; border: 1px solid #ff00ff; color: #ff00ff; text-decoration: none; padding: 10px 20px; border-radius: 5px;">Bot Status</a>
                </div>
            </div>
        </div>
    </div>`;
});"""
    
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(js_content)
        logger.info(f"Created default main.js at {file_path}")
    except Exception as e:
        logger.error(f"Error creating default main.js: {e}")

def create_default_manifest_json(file_path):
    """Create a default manifest.json file."""
    manifest_content = """{
  "short_name": "Vicki",
  "name": "Vicki AI Trading Bot",
  "icons": [
    {
      "src": "/static/images/logo.png",
      "type": "image/png",
      "sizes": "192x192"
    }
  ],
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#121212"
}"""
    
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(manifest_content)
        logger.info(f"Created default manifest.json at {file_path}")
    except Exception as e:
        logger.error(f"Error creating default manifest.json: {e}")

if __name__ == '__main__':
    check_static_files()
    sys.exit(0) 