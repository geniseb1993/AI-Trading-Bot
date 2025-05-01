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
    
    # Create minimal app if necessary
    create_minimal_app_if_missing()
    
    # Ensure frontend serving works
    test_frontend_serving()
    ensure_frontend_serving_files()
    
    logger.info("Render fix script completed successfully")
    return True

if __name__ == "__main__":
    run_render_fix()
