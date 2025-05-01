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
import shutil
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
    
    # Step 2: Copy dashboard_ui.js to the static/js directory and ensure it's available
    logger.info("Step 2: Setting up dashboard_ui.js")
    try:
        dashboard_ui_source = project_root / 'dashboard_ui.js'
        static_js_dir = project_root / 'static' / 'js'
        os.makedirs(static_js_dir, exist_ok=True)
        
        # Destination files
        dashboard_ui_dest1 = static_js_dir / 'dashboard_ui.js'
        dashboard_ui_dest2 = static_js_dir / 'main.js'
        
        # Copy dashboard_ui.js to static/js directory
        if dashboard_ui_source.exists():
            shutil.copy(dashboard_ui_source, dashboard_ui_dest1)
            logger.info(f"Copied dashboard_ui.js to {dashboard_ui_dest1}")
            
            # Also copy as main.js to ensure it's loaded by default
            shutil.copy(dashboard_ui_source, dashboard_ui_dest2)
            logger.info(f"Copied dashboard_ui.js to {dashboard_ui_dest2}")
        else:
            # If dashboard_ui.js doesn't exist, create it from the content in static_js_dir / 'dashboard_ui.js'
            dashboard_ui_src_code = """/**
 * Dashboard UI for Vicki AI Trading Bot
 * This script provides a fallback UI when the React app doesn't load correctly.
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Basic dashboard UI loaded - fallback version');
    const root = document.getElementById('root');
    if (root) {
        // Clear loading indicator
        const loadingEl = document.querySelector('.app-loading');
        if (loadingEl) loadingEl.remove();
        
        // Create simple UI
        root.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; padding: 20px; text-align: center;">
                <h1 style="color: #ff00ff; margin-bottom: 20px;">VICKI AI TRADING BOT</h1>
                <p>Welcome to your AI-powered trading assistant</p>
                <div style="margin-top: 30px; display: flex; gap: 20px;">
                    <a href="/api/health" style="color: #ff00ff; text-decoration: none; border: 1px solid #ff00ff; padding: 10px 20px; border-radius: 4px;">API Health</a>
                    <a href="/api/bot/status" style="color: #ff00ff; text-decoration: none; border: 1px solid #ff00ff; padding: 10px 20px; border-radius: 4px;">Bot Status</a>
                </div>
            </div>
        `;
    }
});"""
            with open(dashboard_ui_dest1, 'w') as f:
                f.write(dashboard_ui_src_code)
            logger.info(f"Created dashboard_ui.js at {dashboard_ui_dest1}")
            
            # Also save as main.js
            with open(dashboard_ui_dest2, 'w') as f:
                f.write(dashboard_ui_src_code)
            logger.info(f"Created main.js (from dashboard UI) at {dashboard_ui_dest2}")
    except Exception as e:
        logger.error(f"Error setting up dashboard_ui.js: {e}")
    
    # Step 3: Copy files to frontend/build
    logger.info("Step 3: Copying files to frontend/build")
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
    
    # Step 4: Ensure dashboard_ui.js is copied to frontend/build as well
    logger.info("Step 4: Copying dashboard_ui.js to frontend/build")
    try:
        frontend_build_js_dir = project_root / 'frontend' / 'build' / 'static' / 'js'
        os.makedirs(frontend_build_js_dir, exist_ok=True)
        
        dashboard_ui_source = static_js_dir / 'dashboard_ui.js'
        dashboard_ui_frontend_dest = frontend_build_js_dir / 'dashboard_ui.js'
        
        if dashboard_ui_source.exists():
            shutil.copy(dashboard_ui_source, dashboard_ui_frontend_dest)
            logger.info(f"Copied dashboard_ui.js to {dashboard_ui_frontend_dest}")
        else:
            logger.warning("dashboard_ui.js not found in static/js directory")
    except Exception as e:
        logger.error(f"Error copying dashboard_ui.js to frontend/build: {e}")
    
    # Step 5: Fix any React placeholders in frontend/build/index.html
    logger.info("Step 5: Fixing React placeholders")
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
    
    # Step 6: Create manifest.json in both static and frontend/build
    logger.info("Step 6: Ensuring manifest.json exists in all required locations")
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
    
    # Step 7: Copy index.html to frontend/build/ if it doesn't exist
    logger.info("Step 7: Ensuring index.html exists in frontend/build")
    try:
        source_index = project_root / 'index.html'
        frontend_index = project_root / 'frontend' / 'build' / 'index.html'
        
        if source_index.exists() and not frontend_index.exists():
            shutil.copy(source_index, frontend_index)
            logger.info(f"Copied index.html to {frontend_index}")
            
            # Fix React placeholders
            fix_react_placeholders(frontend_index)
    except Exception as e:
        logger.error(f"Error copying index.html to frontend/build: {e}")
    
    logger.info("Render deployment preparation completed")
    return True

if __name__ == "__main__":
    success = prepare_render_deployment()
    sys.exit(0 if success else 1) 