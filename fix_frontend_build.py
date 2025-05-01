#!/usr/bin/env python
"""
Fix Frontend Build Script

This script is designed to run after the React frontend is built to fix any issues with file paths
and ensure all necessary assets are included in the build. It:

1. Copies key assets from public/ to frontend/build/ directory if they don't exist
2. Ensures CSS and JS files reference assets with correct relative paths
3. Modifies manifest.json to use correct image paths
"""

import os
import sys
import shutil
import logging
import json
import re
from pathlib import Path
from glob import glob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
BUILD_DIR = os.path.join(FRONTEND_DIR, 'build')
PUBLIC_DIR = os.path.join(FRONTEND_DIR, 'public')
ROOT_PUBLIC_DIR = os.path.join(BASE_DIR, 'public')

def ensure_directories():
    """Ensure all necessary directories exist"""
    dirs = [
        os.path.join(BUILD_DIR, 'images'),
        os.path.join(BUILD_DIR, 'sounds'),
        os.path.join(BUILD_DIR, 'static'),
        os.path.join(BUILD_DIR, 'static', 'css'),
        os.path.join(BUILD_DIR, 'static', 'js'),
        os.path.join(BUILD_DIR, 'static', 'media')
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"Ensured directory exists: {dir_path}")

def copy_assets():
    """Copy all necessary assets to the build directory"""
    # Files to copy from frontend/public to frontend/build
    files_to_copy = [
        ('images', '*.png'),
        ('images', '*.jpg'),
        ('images', '*.jpeg'),
        ('images', '*.svg'),
        ('images', '*.gif'),
        ('sounds', '*.mp3'),
        ('sounds', '*.wav'),
        ('sounds', '*.ogg'),
        ('', 'favicon.ico'),
        ('', 'manifest.json'),
        ('', 'robots.txt'),
        ('', 'logo192.png'),
        ('', 'logo512.png')
    ]
    
    # Copy from frontend/public to frontend/build
    for subdir, pattern in files_to_copy:
        src_dir = os.path.join(PUBLIC_DIR, subdir)
        dst_dir = os.path.join(BUILD_DIR, subdir)
        
        if not os.path.exists(src_dir):
            logger.warning(f"Source directory does not exist: {src_dir}")
            continue
            
        os.makedirs(dst_dir, exist_ok=True)
        
        # Find all matching files and copy them
        for file_path in glob(os.path.join(src_dir, pattern)):
            filename = os.path.basename(file_path)
            dst_path = os.path.join(dst_dir, filename)
            
            # Only copy if file doesn't exist or is newer
            if not os.path.exists(dst_path) or os.path.getmtime(file_path) > os.path.getmtime(dst_path):
                shutil.copy2(file_path, dst_path)
                logger.info(f"Copied {file_path} to {dst_path}")
    
    # Also copy from root public/ to frontend/build
    for subdir, pattern in files_to_copy:
        src_dir = os.path.join(ROOT_PUBLIC_DIR, subdir)
        dst_dir = os.path.join(BUILD_DIR, subdir)
        
        if not os.path.exists(src_dir):
            continue
            
        os.makedirs(dst_dir, exist_ok=True)
        
        for file_path in glob(os.path.join(src_dir, pattern)):
            filename = os.path.basename(file_path)
            dst_path = os.path.join(dst_dir, filename)
            
            # Only copy if not already copied from frontend/public
            if not os.path.exists(dst_path):
                shutil.copy2(file_path, dst_path)
                logger.info(f"Copied {file_path} to {dst_path}")

def fix_manifest():
    """Fix paths in manifest.json"""
    manifest_path = os.path.join(BUILD_DIR, 'manifest.json')
    
    if not os.path.exists(manifest_path):
        logger.warning("manifest.json not found, creating it")
        default_manifest = {
            "short_name": "Vicki",
            "name": "Vicki AI Trading Bot",
            "icons": [
                {
                    "src": "favicon.ico",
                    "sizes": "64x64 32x32 24x24 16x16",
                    "type": "image/x-icon"
                },
                {
                    "src": "images/vicky.png",
                    "type": "image/png",
                    "sizes": "192x192"
                },
                {
                    "src": "images/vicky.png",
                    "type": "image/png",
                    "sizes": "512x512"
                }
            ],
            "start_url": ".",
            "display": "standalone",
            "theme_color": "#000000",
            "background_color": "#ffffff"
        }
        
        with open(manifest_path, 'w') as f:
            json.dump(default_manifest, f, indent=2)
            
        return
        
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
            
        # Check and fix icon paths
        if 'icons' in manifest:
            for icon in manifest['icons']:
                if 'src' in icon:
                    # For each icon referenced in manifest, make sure it exists
                    icon_path = os.path.join(BUILD_DIR, icon['src'])
                    
                    # If it doesn't exist, try to find it in public directories
                    if not os.path.exists(icon_path):
                        filename = os.path.basename(icon['src'])
                        
                        # Check possible alternative locations
                        alt_locations = [
                            os.path.join(PUBLIC_DIR, 'images', filename),
                            os.path.join(PUBLIC_DIR, filename),
                            os.path.join(ROOT_PUBLIC_DIR, 'images', filename),
                            os.path.join(ROOT_PUBLIC_DIR, filename)
                        ]
                        
                        for alt_path in alt_locations:
                            if os.path.exists(alt_path):
                                # If found, copy to build dir and update path
                                img_dir = os.path.dirname(icon_path)
                                os.makedirs(img_dir, exist_ok=True)
                                shutil.copy2(alt_path, icon_path)
                                logger.info(f"Copied icon from {alt_path} to {icon_path}")
                                break
                        
                        # If still not found and it's a logo, use vicky.png as fallback
                        if not os.path.exists(icon_path) and ('logo' in filename.lower() or 'icon' in filename.lower()):
                            vicky_paths = [
                                os.path.join(BUILD_DIR, 'images', 'vicky.png'),
                                os.path.join(PUBLIC_DIR, 'images', 'vicky.png'),
                                os.path.join(ROOT_PUBLIC_DIR, 'images', 'vicky.png')
                            ]
                            
                            for vicky_path in vicky_paths:
                                if os.path.exists(vicky_path):
                                    img_dir = os.path.dirname(icon_path)
                                    os.makedirs(img_dir, exist_ok=True)
                                    shutil.copy2(vicky_path, icon_path)
                                    logger.info(f"Using vicky.png as fallback for {icon['src']}")
                                    break
        
        # Write the updated manifest
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
            
        logger.info("Updated manifest.json")
    except Exception as e:
        logger.error(f"Error fixing manifest.json: {str(e)}")

def fix_index_html():
    """Fix paths in index.html"""
    index_path = os.path.join(BUILD_DIR, 'index.html')
    
    if not os.path.exists(index_path):
        logger.error("index.html not found, frontend build may be missing")
        return
        
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Ensure velma.png references are corrected
        if 'velma.png' in content and not os.path.exists(os.path.join(BUILD_DIR, 'images', 'velma.png')):
            # Try to find velma.png in possible locations
            for velma_path in [
                os.path.join(PUBLIC_DIR, 'images', 'velma.png'),
                os.path.join(ROOT_PUBLIC_DIR, 'images', 'velma.png')
            ]:
                if os.path.exists(velma_path):
                    dst_dir = os.path.join(BUILD_DIR, 'images')
                    os.makedirs(dst_dir, exist_ok=True)
                    dst_path = os.path.join(dst_dir, 'velma.png')
                    shutil.copy2(velma_path, dst_path)
                    logger.info(f"Copied velma.png from {velma_path} to {dst_path}")
                    break
                    
        # If no velma.png found, try to use vicky.png as a fallback
        if not os.path.exists(os.path.join(BUILD_DIR, 'images', 'velma.png')):
            for vicky_path in [
                os.path.join(BUILD_DIR, 'images', 'vicky.png'),
                os.path.join(PUBLIC_DIR, 'images', 'vicky.png'),
                os.path.join(ROOT_PUBLIC_DIR, 'images', 'vicky.png')
            ]:
                if os.path.exists(vicky_path):
                    dst_dir = os.path.join(BUILD_DIR, 'images')
                    os.makedirs(dst_dir, exist_ok=True)
                    dst_path = os.path.join(dst_dir, 'velma.png')
                    shutil.copy2(vicky_path, dst_path)
                    logger.info(f"Using vicky.png as fallback for velma.png")
                    break
                    
        logger.info("Checked index.html for references to images")
    except Exception as e:
        logger.error(f"Error fixing index.html: {str(e)}")

def fix_css_files():
    """Fix paths in CSS files"""
    css_files = glob(os.path.join(BUILD_DIR, 'static', 'css', '*.css'))
    
    for css_file in css_files:
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Fix any URL references to images
            content = re.sub(r'url\([\'"]?(?!data:|http|\/static)([^\'")]+)[\'"]?\)', r'url("/images/\1")', content)
            
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info(f"Fixed CSS file: {css_file}")
        except Exception as e:
            logger.error(f"Error fixing CSS file {css_file}: {str(e)}")

def main():
    """Main function to fix frontend build"""
    logger.info("Starting frontend build fixes")
    
    if not os.path.exists(BUILD_DIR):
        logger.error(f"Build directory not found: {BUILD_DIR}")
        return False
        
    # Ensure all necessary directories exist
    ensure_directories()
    
    # Copy assets from public directories to build
    copy_assets()
    
    # Fix manifest.json
    fix_manifest()
    
    # Fix index.html
    fix_index_html()
    
    # Fix CSS files
    fix_css_files()
    
    logger.info("Frontend build fixes completed successfully")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 