from flask import Blueprint, jsonify, current_app
from datetime import datetime
import logging
import os
import sys
import platform
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional dependency - we'll check if it's available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    logger.warning("psutil module not found. Some health check features will be limited.")

health_routes = Blueprint('health_routes', __name__)

@health_routes.route('/', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'message': 'AI Trading Bot API is running'
    })

@health_routes.route('/detailed', methods=['GET'])
def detailed_health():
    """Detailed health check with system information."""
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'message': 'AI Trading Bot API is running',
        'python_version': python_version,
        'environment': os.environ.get('FLASK_ENV', 'default'),
        'debug': os.environ.get('FLASK_DEBUG', '0') == '1'
    })

@health_routes.route('/static-files', methods=['GET'])
def static_files_check():
    """Check the existence and path of static files."""
    project_root = Path(os.getcwd())
    
    # Important static files to check
    file_paths = {
        'index_html': project_root / 'index.html',
        'static_index_html': project_root / 'static' / 'index.html',
        'frontend_build_index': project_root / 'frontend' / 'build' / 'index.html',
        'static_css': project_root / 'static' / 'css' / 'main.css',
        'static_js': project_root / 'static' / 'js' / 'main.js',
        'static_manifest': project_root / 'static' / 'manifest.json',
        'frontend_static_css': project_root / 'frontend' / 'build' / 'static' / 'css' / 'main.css',
        'frontend_static_js': project_root / 'frontend' / 'build' / 'static' / 'js' / 'main.js',
        'frontend_manifest': project_root / 'frontend' / 'build' / 'manifest.json'
    }
    
    # Check each file
    file_status = {}
    for name, path in file_paths.items():
        exists = path.exists()
        file_status[name] = {
            'exists': exists,
            'path': str(path),
            'size': os.path.getsize(path) if exists else 0
        }
    
    # Check Flask static folder configuration
    flask_config = {
        'static_folder': current_app.static_folder,
        'static_url_path': current_app.static_url_path
    }
    
    # Run our preparation script if files are missing
    missing_files = [name for name, status in file_status.items() if not status['exists']]
    if missing_files:
        try:
            # Import and run the preparation function
            sys.path.append(str(project_root))
            from prepare_render_deployment import prepare_render_deployment
            preparation_result = prepare_render_deployment()
            
            # Update file status after preparation
            for name, path in file_paths.items():
                exists = path.exists()
                file_status[name] = {
                    'exists': exists,
                    'path': str(path),
                    'size': os.path.getsize(path) if exists else 0,
                    'fixed': exists and name in missing_files
                }
        except Exception as e:
            file_status['preparation_error'] = str(e)
    
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'file_status': file_status,
        'flask_config': flask_config,
        'environment_vars': {
            'SERVE_FRONTEND': os.environ.get('SERVE_FRONTEND', ''),
            'FLASK_ENV': os.environ.get('FLASK_ENV', ''),
            'PATH_DEBUG': os.environ.get('PATH_DEBUG', '')
        }
    })

@health_routes.route('/ping', methods=['GET'])
def ping():
    """Simple ping endpoint for quick connectivity checks"""
    return jsonify({'ping': 'pong', 'timestamp': datetime.now().isoformat()}), 200 