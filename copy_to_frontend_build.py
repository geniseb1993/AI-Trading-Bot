#!/usr/bin/env python
"""
Copy files to frontend/build

This script copies all necessary static files to the frontend/build directory
to ensure they are available for serving by Flask.
"""

import os
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_react_placeholders(file_path):
    """Fix React placeholder variables in HTML files."""
    try:
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Replace React placeholder variables
        replacements = {
            '%PUBLIC_URL%': '',
            '%PUBLIC_URL%/': '/',
            '%PUBLIC_URL%/manifest.json': '/static/manifest.json',
            '%PUBLIC_URL%/logo192.png': '/static/images/logo.png',
            '%PUBLIC_URL%/images/': '/static/images/',
            '"%PUBLIC_URL%/': '"/static/'
        }
        
        fixed_content = content
        for old, new in replacements.items():
            fixed_content = fixed_content.replace(old, new)
        
        # Write back if changes were made
        if content != fixed_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            logger.info(f"Fixed React placeholders in {file_path}")
            return True
        
        return False
    except Exception as e:
        logger.error(f"Error fixing React placeholders in {file_path}: {e}")
        return False

def copy_to_frontend_build():
    """Copy all necessary files to frontend/build directory."""
    try:
        # Get the project root directory
        project_root = Path(os.getcwd())
        
        # Define directories
        static_dir = project_root / 'static'
        frontend_dir = project_root / 'frontend'
        frontend_public_dir = frontend_dir / 'public'
        frontend_build_dir = frontend_dir / 'build'
        frontend_build_static_dir = frontend_build_dir / 'static'
        frontend_build_css_dir = frontend_build_static_dir / 'css'
        frontend_build_js_dir = frontend_build_static_dir / 'js'
        frontend_build_images_dir = frontend_build_static_dir / 'images'
        
        # Create frontend build directories
        for directory in [
            frontend_dir, 
            frontend_build_dir, 
            frontend_build_static_dir,
            frontend_build_css_dir,
            frontend_build_js_dir,
            frontend_build_images_dir
        ]:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        
        # Copy index.html to frontend/build
        index_path = project_root / 'index.html'
        if index_path.exists():
            shutil.copy(index_path, frontend_build_dir / 'index.html')
            logger.info(f"Copied {index_path} to {frontend_build_dir / 'index.html'}")
            # Fix any React placeholders in the copied file
            fix_react_placeholders(frontend_build_dir / 'index.html')
        else:
            logger.warning(f"index.html not found at {index_path}")
        
        # Copy static files to frontend/build/static
        if static_dir.exists():
            # Copy CSS files
            if (static_dir / 'css').exists():
                for file in (static_dir / 'css').glob('*'):
                    shutil.copy(file, frontend_build_css_dir / file.name)
                    logger.info(f"Copied {file} to {frontend_build_css_dir / file.name}")
            
            # Copy JS files
            if (static_dir / 'js').exists():
                for file in (static_dir / 'js').glob('*'):
                    shutil.copy(file, frontend_build_js_dir / file.name)
                    logger.info(f"Copied {file} to {frontend_build_js_dir / file.name}")
            
            # Copy image files
            if (static_dir / 'images').exists():
                for file in (static_dir / 'images').glob('*'):
                    shutil.copy(file, frontend_build_images_dir / file.name)
                    logger.info(f"Copied {file} to {frontend_build_images_dir / file.name}")
        else:
            logger.warning(f"Static directory not found at {static_dir}")
        
        # Copy frontend/public files to frontend/build as well
        if frontend_public_dir.exists():
            # Get all files in frontend/public
            for file in frontend_public_dir.glob('*'):
                if file.is_file():
                    shutil.copy(file, frontend_build_dir / file.name)
                    logger.info(f"Copied {file} to {frontend_build_dir / file.name}")
            
            # Copy frontend/public/images to frontend/build/images
            if (frontend_public_dir / 'images').exists():
                for file in (frontend_public_dir / 'images').glob('*'):
                    shutil.copy(file, frontend_build_images_dir / file.name)
                    logger.info(f"Copied {file} to {frontend_build_images_dir / file.name}")
        else:
            logger.warning(f"Frontend public directory not found at {frontend_public_dir}")
        
        # If frontend/build/static/css/main.css doesn't exist, create a basic one
        main_css_path = frontend_build_css_dir / 'main.css'
        if not main_css_path.exists():
            with open(main_css_path, 'w') as f:
                f.write("""
/* Basic CSS for Vicki AI Trading Bot */
body {
    font-family: Arial, sans-serif;
    background-color: #121212;
    color: #ffffff;
    margin: 0;
    padding: 0;
}
#root {
    min-height: 100vh;
}
a {
    color: #61dafb;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}
""")
            logger.info(f"Created basic main.css at {main_css_path}")
        
        # If frontend/build/static/js/main.js doesn't exist, create a basic one
        main_js_path = frontend_build_js_dir / 'main.js'
        if not main_js_path.exists():
            # Try to copy the dashboard UI file instead of creating a basic one
            dashboard_ui_path = project_root / 'dashboard_ui.js'
            if dashboard_ui_path.exists():
                # If dashboard_ui.js exists, copy it as main.js
                shutil.copy(dashboard_ui_path, main_js_path)
                logger.info(f"Copied dashboard UI to {main_js_path}")
            else:
                # Create a basic main.js if dashboard_ui.js doesn't exist
                with open(main_js_path, 'w') as f:
                    f.write("""
// Basic JS for Vicki AI Trading Bot
console.log('Vicki AI Trading Bot loaded');
""")
                logger.info(f"Created basic main.js at {main_js_path}")
        
        # Fix React placeholders in any HTML files in frontend/build
        for html_file in frontend_build_dir.glob('*.html'):
            fix_react_placeholders(html_file)
        
        # Also make sure manifest.json is properly available
        manifest_path = static_dir / 'manifest.json'
        if manifest_path.exists():
            # Copy to both locations to be safe
            shutil.copy(manifest_path, frontend_build_dir / 'manifest.json')
            logger.info(f"Copied {manifest_path} to {frontend_build_dir / 'manifest.json'}")
            
            # Also copy to frontend/build/static
            shutil.copy(manifest_path, frontend_build_static_dir / 'manifest.json')
            logger.info(f"Copied {manifest_path} to {frontend_build_static_dir / 'manifest.json'}")
        
        logger.info("Successfully copied files to frontend/build")
        return True
    
    except Exception as e:
        logger.error(f"Error copying files to frontend/build: {e}")
        return False

if __name__ == "__main__":
    copy_to_frontend_build() 