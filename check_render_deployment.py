#!/usr/bin/env python
"""
Check Render Deployment

This script verifies that all necessary files for Render deployment exist
and are correctly configured.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_render_deployment():
    """Check that all necessary files for Render deployment exist."""
    # Get the base directory
    base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    logger.info(f"Base directory: {base_dir}")
    
    # List of required files
    required_files = [
        'app.py',
        'wsgi.py',
        'Procfile',
        'render.yaml',
        'requirements.txt'
    ]
    
    # Check each required file
    for file in required_files:
        file_path = base_dir / file
        if file_path.exists():
            logger.info(f"✅ {file} found")
        else:
            logger.error(f"❌ {file} not found")
    
    # Check wsgi.py content
    wsgi_path = base_dir / 'wsgi.py'
    if wsgi_path.exists():
        with open(wsgi_path, 'r') as f:
            content = f.read()
            if 'app = application' in content:
                logger.info("✅ wsgi.py has correct app = application definition")
            else:
                logger.warning("⚠️ wsgi.py does not contain 'app = application' statement")
    
    # Check render.yaml content
    render_path = base_dir / 'render.yaml'
    if render_path.exists():
        with open(render_path, 'r') as f:
            content = f.read()
            if 'gunicorn app:appgunicorn' in content:
                logger.error("❌ render.yaml contains incorrect gunicorn command: 'gunicorn app:appgunicorn'")
            elif 'gunicorn wsgi:app' in content:
                logger.info("✅ render.yaml has correct gunicorn command: 'gunicorn wsgi:app'")
            else:
                logger.warning("⚠️ render.yaml does not contain 'gunicorn wsgi:app' command")
    
    # Check Procfile content
    procfile_path = base_dir / 'Procfile'
    if procfile_path.exists():
        with open(procfile_path, 'r') as f:
            content = f.read()
            if 'gunicorn wsgi:app' in content:
                logger.info("✅ Procfile has correct gunicorn command: 'gunicorn wsgi:app'")
            else:
                logger.warning("⚠️ Procfile does not contain 'gunicorn wsgi:app' command")
    
    # Check if .render directory exists
    render_dir = base_dir / '.render'
    if render_dir.exists():
        logger.info("✅ .render directory exists")
        
        # Check if build.yaml exists
        build_yaml = render_dir / 'build.yaml'
        if build_yaml.exists():
            logger.info("✅ .render/build.yaml exists")
            with open(build_yaml, 'r') as f:
                content = f.read()
                if 'startCommand: gunicorn wsgi:app' in content:
                    logger.info("✅ .render/build.yaml has correct gunicorn command")
                else:
                    logger.warning("⚠️ .render/build.yaml does not have correct gunicorn command")
        else:
            logger.warning("⚠️ .render/build.yaml does not exist")
    else:
        logger.warning("⚠️ .render directory does not exist")
    
    logger.info("Deployment check complete!")

if __name__ == '__main__':
    check_render_deployment() 