#!/usr/bin/env python
"""
Import Path Updater

This script updates import paths in Python files from 'api.' to 'backend.'
after migrating files to the new directory structure.
"""

import os
import re
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('update_imports')

def update_imports_in_file(file_path):
    """Update import paths from 'api.' to 'backend.' in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns to replace
        patterns = [
            (r'from\s+api\.', 'from backend.'),
            (r'import\s+api\.', 'import backend.'),
        ]
        
        original_content = content
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Updated imports in: {file_path}")
            return True
        else:
            logger.debug(f"No import paths to update in: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error updating imports in {file_path}: {e}")
        return False

def process_directory(directory):
    """Process all Python files in a directory and its subdirectories"""
    updated_files = 0
    
    # Get all Python files
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if update_imports_in_file(file_path):
                    updated_files += 1
    
    return updated_files

def main():
    """Main function"""
    # Get the backend directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    backend_dir = os.path.join(base_dir, 'backend')
    
    if not os.path.exists(backend_dir):
        logger.error(f"Backend directory not found: {backend_dir}")
        logger.error("Run the migration script first to create the backend directory structure.")
        return 1
    
    logger.info(f"Processing directory: {backend_dir}")
    updated_files = process_directory(backend_dir)
    
    logger.info(f"Import paths updated in {updated_files} files.")
    logger.info("Remember to check the updated files to ensure all imports are correct.")
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 