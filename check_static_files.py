#!/usr/bin/env python
"""
Static Files Verification Script

This script checks that static files are correctly organized for Render
deployment and reports any issues.
"""

import os
import sys
import json
from pathlib import Path

def colorize(text, color):
    """Add color to terminal output"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'reset': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"

def log_success(message):
    print(colorize(f"✅ {message}", 'green'))

def log_warning(message):
    print(colorize(f"⚠️ {message}", 'yellow'))

def log_error(message):
    print(colorize(f"❌ {message}", 'red'))

def log_info(message):
    print(colorize(f"ℹ️ {message}", 'blue'))

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / 'static'
FRONTEND_BUILD = BASE_DIR / 'frontend' / 'build'

def check_directory_exists(path, name):
    """Check if directory exists and report"""
    if path.exists():
        if path.is_dir():
            log_success(f"{name} directory exists at {path}")
            return True
        else:
            log_error(f"{name} exists but is not a directory: {path}")
            return False
    else:
        log_error(f"{name} directory does not exist: {path}")
        return False

def count_files(directory, extension=None):
    """Count files in directory, optionally filter by extension"""
    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if extension is None or file.endswith(extension):
                count += 1
    return count

def check_required_files():
    """Check for required files in static directory"""
    # Check index.html
    index_path = STATIC_DIR / 'index.html'
    if index_path.exists():
        log_success(f"Found index.html ({index_path.stat().st_size} bytes)")
    else:
        log_error(f"Missing index.html in {STATIC_DIR}")
    
    # Check JS files
    js_dir = STATIC_DIR / 'js'
    if js_dir.exists():
        js_count = count_files(js_dir, '.js')
        if js_count > 0:
            log_success(f"Found {js_count} JavaScript files in {js_dir}")
        else:
            log_warning(f"No JavaScript files found in {js_dir}")
    else:
        js_count = 0
        log_error(f"Missing js directory in {STATIC_DIR}")
    
    # Check CSS files
    css_dir = STATIC_DIR / 'css'
    if css_dir.exists():
        css_count = count_files(css_dir, '.css')
        if css_count > 0:
            log_success(f"Found {css_count} CSS files in {css_dir}")
        else:
            log_warning(f"No CSS files found in {css_dir}")
    else:
        css_count = 0
        log_error(f"Missing css directory in {STATIC_DIR}")
    
    # Check for manifest.json (typically needed for PWAs)
    manifest_path = STATIC_DIR / 'manifest.json'
    if manifest_path.exists():
        log_success(f"Found manifest.json")
    else:
        log_warning(f"Missing manifest.json in {STATIC_DIR}")
    
    return js_count > 0 and css_count > 0 and index_path.exists()

def check_nested_static():
    """Check for problematic nested static directories"""
    nested_static = STATIC_DIR / 'static'
    if nested_static.exists():
        log_error(f"Problematic nested static directory found: {nested_static}")
        return False
    return True

def compare_with_frontend_build():
    """Compare static directory with frontend build to identify missing files"""
    if not FRONTEND_BUILD.exists():
        log_warning(f"Frontend build directory not found: {FRONTEND_BUILD}")
        return
    
    # Compare file counts
    static_count = count_files(STATIC_DIR)
    build_count = count_files(FRONTEND_BUILD)
    
    log_info(f"Static directory contains {static_count} files")
    log_info(f"Frontend build directory contains {build_count} files")
    
    if static_count < build_count * 0.7:  # Allow for some differences
        log_warning(f"Static directory may be missing files from frontend build")
    
    # Check for asset-manifest.json
    asset_manifest = FRONTEND_BUILD / 'asset-manifest.json'
    if asset_manifest.exists():
        try:
            with open(asset_manifest, 'r') as f:
                manifest = json.load(f)
            
            # Check if main entries are copied to static
            if 'files' in manifest:
                for key, file_path in manifest['files'].items():
                    if file_path.startswith('/'):
                        file_path = file_path[1:]  # Remove leading slash
                    
                    static_file = STATIC_DIR / file_path
                    if not static_file.exists():
                        log_warning(f"Missing file from asset manifest: {file_path}")
        except json.JSONDecodeError:
            log_error(f"Could not parse asset-manifest.json")
        except Exception as e:
            log_error(f"Error checking asset manifest: {str(e)}")

def main():
    """Main function"""
    print("\n" + "="*80)
    print(colorize("STATIC FILES VERIFICATION", 'blue'))
    print("="*80 + "\n")
    
    # Check if static directory exists
    if not check_directory_exists(STATIC_DIR, "Static"):
        sys.exit(1)
    
    # Check if frontend build directory exists
    check_directory_exists(FRONTEND_BUILD, "Frontend build")
    
    # Check for required files
    files_ok = check_required_files()
    
    # Check for nested static directory
    nested_ok = check_nested_static()
    
    # Compare with frontend build
    compare_with_frontend_build()
    
    print("\n" + "="*80)
    if files_ok and nested_ok:
        log_success("STATIC FILES VERIFICATION PASSED")
    else:
        log_error("STATIC FILES VERIFICATION FAILED - See issues above")
    print("="*80 + "\n")
    
    return 0 if files_ok and nested_ok else 1

if __name__ == "__main__":
    sys.exit(main()) 