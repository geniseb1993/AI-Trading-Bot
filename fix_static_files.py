#!/usr/bin/env python
"""
Static Files Cleanup and Organization Script for Render Deployment

This script:
1. Removes duplicate static directories
2. Ensures frontend build files are properly copied to the static directory
3. Creates a clean structure for Render to serve static files
"""

import os
import shutil
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define paths
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_BUILD = BASE_DIR / 'frontend' / 'build'
STATIC_DIR = BASE_DIR / 'static'
TEMP_DIR = BASE_DIR / 'temp_static'

def clean_static_directories():
    """Remove duplicate and nested static directories"""
    logger.info("Cleaning up static directories...")
    
    # Remove nested static/static directory if it exists
    nested_static = STATIC_DIR / 'static'
    if nested_static.exists():
        logger.info(f"Removing nested static directory: {nested_static}")
        shutil.rmtree(nested_static)
    
    # Create temporary directory for reorganization
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    TEMP_DIR.mkdir(exist_ok=True)
    
    # Move any existing non-nested static content to temp
    if STATIC_DIR.exists():
        for item in STATIC_DIR.iterdir():
            if item.name != 'static':  # Skip nested static folder
                dest = TEMP_DIR / item.name
                logger.info(f"Moving {item} to {dest}")
                
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
        
        # Clear the static directory
        shutil.rmtree(STATIC_DIR)
        STATIC_DIR.mkdir(exist_ok=True)

def copy_frontend_build():
    """Copy frontend build files to static directory"""
    logger.info("Copying frontend build files to static directory...")
    
    if not FRONTEND_BUILD.exists():
        logger.error(f"Frontend build directory not found: {FRONTEND_BUILD}")
        return False
    
    # Copy all files from frontend/build to static directory
    for item in FRONTEND_BUILD.iterdir():
        dest = STATIC_DIR / item.name
        
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)
    
    # Move any non-duplicate content from temp back to static
    if TEMP_DIR.exists():
        for item in TEMP_DIR.iterdir():
            dest = STATIC_DIR / item.name
            
            if not dest.exists():
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
            else:
                logger.info(f"Skipping {item} as it already exists in static directory")
    
    return True

def ensure_required_directories():
    """Ensure all required directories exist"""
    required_dirs = [
        STATIC_DIR / 'css',
        STATIC_DIR / 'js',
        STATIC_DIR / 'images',
        BASE_DIR / 'data' / 'logs',
        BASE_DIR / 'data' / 'broker',
        BASE_DIR / 'data' / 'market_data'
    ]
    
    for directory in required_dirs:
        directory.mkdir(exist_ok=True, parents=True)
        logger.info(f"Ensured directory exists: {directory}")

def cleanup():
    """Clean up temporary resources"""
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
        logger.info(f"Removed temporary directory: {TEMP_DIR}")

def main():
    """Main execution function"""
    logger.info("Starting static files cleanup and organization...")
    
    try:
        clean_static_directories()
        success = copy_frontend_build()
        if success:
            ensure_required_directories()
            logger.info("Static files successfully reorganized!")
        else:
            logger.error("Failed to copy frontend build files. Check if they exist.")
    except Exception as e:
        logger.error(f"Error during static files reorganization: {str(e)}")
    finally:
        cleanup()

if __name__ == "__main__":
    main() 