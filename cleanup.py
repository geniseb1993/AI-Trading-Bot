#!/usr/bin/env python3
"""
Cleanup Script

This script removes unnecessary test files and scripts to clean up the project.
Only files that don't affect the core functionality are removed.
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
logger = logging.getLogger('cleanup')

# Files to keep (essential files)
ESSENTIAL_FILES = [
    # Core Python files
    'app.py',
    'wsgi.py',
    'config.py',
    'render_fix.py',
    'install_mock_modules.py',
    'check_requirements.py',
    'cleanup.py',
    
    # Configuration files
    'requirements.txt',
    'render.yaml',
    'Procfile',
    '.env.example',
    '.gitignore',
    
    # Documentation
    'README.md',
    'CHANGELOG.md',
]

# Directories to keep
ESSENTIAL_DIRS = [
    'api',
    'mock_modules',
    'frontend',
    'static',
    'templates',
    'execution_model',
    'config',
    'dual_bot',
]

# Files and directories to explicitly remove
FILES_TO_REMOVE = [
    # Test files
    'test_*.py',
    'test-*.py',
    '*_test.py',
    
    # Development and debugging scripts
    'fix-*.py',
    'fix_*.py',
    'check_*.py',
    'test_*.bat',
    'test_*.sh',
    'test-*.bat',
    'test-*.sh',
    
    # Backup files
    '*.bak',
    '*.backup',
    '*.old',
    
    # Logs
    '*.log',
]

DIRS_TO_REMOVE = [
    'tests',
    'backup_scripts',
    '__pycache__',
]

def is_test_file(filename):
    """Check if a file is a test file based on naming patterns"""
    name = filename.lower()
    return (name.startswith('test_') or 
            name.startswith('test-') or 
            name.endswith('_test.py') or
            ('test' in name and name.endswith('.py')))

def is_essential_file(path):
    """Check if a file is essential and should be kept"""
    filename = os.path.basename(path)
    
    # Check if it's in the essential files list
    if filename in ESSENTIAL_FILES:
        return True
        
    # Check file extensions to keep
    if filename.endswith(('.md', '.json', '.yaml', '.yml')):
        return True
        
    return False

def should_remove_file(path):
    """Check if a file should be removed"""
    if is_essential_file(path):
        return False
    
    filename = os.path.basename(path)
    
    # Check if it matches any pattern in FILES_TO_REMOVE
    for pattern in FILES_TO_REMOVE:
        if pattern.startswith('*') and pattern.endswith('*'):
            # Pattern like *word*
            substring = pattern.strip('*')
            if substring in filename:
                return True
        elif pattern.startswith('*'):
            # Pattern like *.extension
            suffix = pattern[1:]
            if filename.endswith(suffix):
                return True
        elif pattern.endswith('*'):
            # Pattern like prefix*
            prefix = pattern[:-1]
            if filename.startswith(prefix):
                return True
        elif pattern == filename:
            # Exact match
            return True
    
    return is_test_file(filename)

def should_remove_directory(path):
    """Check if a directory should be removed"""
    dirname = os.path.basename(path)
    
    # Check essential directories
    if dirname in ESSENTIAL_DIRS:
        return False
    
    # Check directories to remove
    if dirname in DIRS_TO_REMOVE:
        return True
    
    # Don't remove directories with underscores (likely module directories)
    if '_' in dirname and not dirname.startswith('__'):
        return False
    
    return False

def scan_directory(directory, simulate=True):
    """Scan a directory and remove unnecessary files"""
    removed_files = []
    removed_dirs = []
    
    # First scan files
    for root, dirs, files in os.walk(directory, topdown=False):
        # Check files
        for file in files:
            filepath = os.path.join(root, file)
            if should_remove_file(filepath):
                if not simulate:
                    try:
                        os.remove(filepath)
                        logger.info(f"Removed file: {filepath}")
                    except Exception as e:
                        logger.error(f"Failed to remove {filepath}: {e}")
                removed_files.append(filepath)
        
        # Check directories
        for dir in dirs:
            dirpath = os.path.join(root, dir)
            if should_remove_directory(dirpath):
                if not simulate:
                    try:
                        shutil.rmtree(dirpath)
                        logger.info(f"Removed directory: {dirpath}")
                    except Exception as e:
                        logger.error(f"Failed to remove directory {dirpath}: {e}")
                removed_dirs.append(dirpath)
    
    return removed_files, removed_dirs

def run_cleanup(simulate=True):
    """Run the cleanup process"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"Starting cleanup in {base_dir}" + (" (simulation mode)" if simulate else ""))
    
    removed_files, removed_dirs = scan_directory(base_dir, simulate)
    
    logger.info(f"Files marked for removal: {len(removed_files)}")
    logger.info(f"Directories marked for removal: {len(removed_dirs)}")
    
    if simulate:
        # Print summary of what would be removed
        for file in removed_files[:10]:  # Show top 10 files
            logger.info(f"Would remove file: {os.path.relpath(file, base_dir)}")
        
        if len(removed_files) > 10:
            logger.info(f"... and {len(removed_files) - 10} more files")
        
        for dir in removed_dirs:
            logger.info(f"Would remove directory: {os.path.relpath(dir, base_dir)}")
        
        logger.info("This was a simulation. Run with --force to actually remove files.")
    else:
        logger.info("Cleanup completed successfully.")
    
    return removed_files, removed_dirs

if __name__ == "__main__":
    # Check if we're in force mode
    force = len(sys.argv) > 1 and sys.argv[1] == '--force'
    run_cleanup(simulate=not force) 