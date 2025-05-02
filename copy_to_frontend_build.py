#!/usr/bin/env python
"""
Copy Frontend Build to Static Directory

This script copies the React frontend build files to the Flask static directory
to ensure the frontend is properly served by the backend.
"""

import os
import shutil
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("frontend_build_copier")

def ensure_directory_exists(directory_path):
    """Make sure the directory exists, creating it if necessary"""
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path.exists()

def copy_directory_contents(source_dir, dest_dir):
    """Copy all contents from source directory to destination directory"""
    if not os.path.exists(source_dir):
        logger.error(f"Source directory {source_dir} does not exist")
        return False
    
    if not os.path.exists(dest_dir):
        ensure_directory_exists(dest_dir)
    
    # Count files copied for reporting
    file_count = 0
    
    # Walk through all files and directories in source
    for root, dirs, files in os.walk(source_dir):
        # Calculate the relative path from source to the current location
        rel_path = os.path.relpath(root, source_dir)
        
        # Create the corresponding directory in destination
        if rel_path != '.':
            target_dir = os.path.join(dest_dir, rel_path)
            ensure_directory_exists(target_dir)
        else:
            target_dir = dest_dir
        
        # Copy each file to destination
        for file in files:
            source_file = os.path.join(root, file)
            dest_file = os.path.join(target_dir, file)
            
            try:
                shutil.copy2(source_file, dest_file)
                file_count += 1
            except Exception as e:
                logger.error(f"Error copying {source_file} to {dest_file}: {str(e)}")
    
    logger.info(f"Copied {file_count} files from {source_dir} to {dest_dir}")
    return True

def main():
    """Main function to copy the frontend build to static directory"""
    logger.info("Starting frontend build copy process")
    
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_build_dir = os.path.join(base_dir, 'frontend', 'build')
    static_dir = os.path.join(base_dir, 'static')
    
    # Check if frontend build exists
    if not os.path.exists(frontend_build_dir):
        logger.warning(f"Frontend build directory not found at {frontend_build_dir}")
        
        # Try an alternate location
        alternate_build_dir = os.path.join(base_dir, 'build')
        if os.path.exists(alternate_build_dir):
            logger.info(f"Found alternate build directory at {alternate_build_dir}")
            frontend_build_dir = alternate_build_dir
        else:
            logger.error("Could not find frontend build directory")
            return False
    
    # Create static directory if it doesn't exist
    ensure_directory_exists(static_dir)
    
    # Copy main static files
    success = copy_directory_contents(frontend_build_dir, static_dir)
    
    # Copy nested static directory if it exists
    nested_static_dir = os.path.join(frontend_build_dir, 'static')
    static_css_dir = os.path.join(static_dir, 'css')
    static_js_dir = os.path.join(static_dir, 'js')
    
    # Ensure static/css and static/js exist
    ensure_directory_exists(static_css_dir)
    ensure_directory_exists(static_js_dir)
    
    # Copy nested static directories if they exist
    if os.path.exists(os.path.join(nested_static_dir, 'css')):
        copy_directory_contents(os.path.join(nested_static_dir, 'css'), static_css_dir)
    
    if os.path.exists(os.path.join(nested_static_dir, 'js')):
        copy_directory_contents(os.path.join(nested_static_dir, 'js'), static_js_dir)
    
    logger.info("Frontend build copy process completed")
    return success

if __name__ == "__main__":
    main() 