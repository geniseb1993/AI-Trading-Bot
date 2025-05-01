#!/usr/bin/env python
"""
Prepare Render Deployment

This script prepares the app for deployment on Render by:
1. Setting up static files
2. Copying them to the frontend/build directory
3. Ensuring all paths are correctly configured

Run this script as part of the Render build process.
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def prepare_render_deployment():
    """Prepare the app for deployment on Render."""
    logger.info("Starting Render deployment preparation")
    
    # Get the project root directory
    project_root = Path(os.getcwd())
    logger.info(f"Project root: {project_root}")
    
    # Step 1: Set up static files
    logger.info("Step 1: Setting up static files")
    try:
        # Import directly from the file
        from setup_static_files import setup_static_files
        setup_result = setup_static_files()
        if setup_result:
            logger.info("Static files setup completed successfully")
        else:
            logger.error("Static files setup failed")
            return False
    except Exception as e:
        logger.error(f"Error setting up static files: {e}")
        return False
    
    # Step 2: Copy files to frontend/build
    logger.info("Step 2: Copying files to frontend/build")
    try:
        from copy_to_frontend_build import copy_to_frontend_build, fix_react_placeholders
        copy_result = copy_to_frontend_build()
        if copy_result:
            logger.info("Files copied to frontend/build successfully")
        else:
            logger.error("Failed to copy files to frontend/build")
            return False
    except Exception as e:
        logger.error(f"Error copying files to frontend/build: {e}")
        return False
    
    # Step 3: Fix any React placeholders in frontend/build/index.html
    logger.info("Step 3: Fixing React placeholders")
    try:
        frontend_index = project_root / 'frontend' / 'build' / 'index.html'
        if frontend_index.exists():
            fix_result = fix_react_placeholders(frontend_index)
            if fix_result:
                logger.info("React placeholders fixed successfully")
            else:
                logger.info("No React placeholders needed fixing")
        else:
            logger.warning(f"index.html not found at {frontend_index}")
    except Exception as e:
        logger.error(f"Error fixing React placeholders: {e}")
    
    # Step 4: Create manifest.json in both static and frontend/build
    logger.info("Step 4: Ensuring manifest.json exists in all required locations")
    try:
        static_manifest = project_root / 'static' / 'manifest.json'
        frontend_manifest = project_root / 'frontend' / 'build' / 'manifest.json'
        frontend_static_manifest = project_root / 'frontend' / 'build' / 'static' / 'manifest.json'
        
        # Create directories if they don't exist
        os.makedirs(project_root / 'frontend' / 'build' / 'static', exist_ok=True)
        
        # Create manifest content
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
        
        # Write manifest to all locations
        for manifest_path in [static_manifest, frontend_manifest, frontend_static_manifest]:
            with open(manifest_path, 'w') as f:
                f.write(manifest_content)
            logger.info(f"Created manifest.json at {manifest_path}")
    except Exception as e:
        logger.error(f"Error creating manifest.json: {e}")
    
    logger.info("Render deployment preparation completed")
    return True

if __name__ == "__main__":
    success = prepare_render_deployment()
    sys.exit(0 if success else 1) 