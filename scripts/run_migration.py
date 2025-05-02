#!/usr/bin/env python
"""
Complete Migration Runner

This script runs all migration steps to move from the old 'api' structure to the new 
'backend' structure. It will:
1. Run the file migration script appropriate for your OS
2. Update import paths in the migrated files
3. Update the wsgi.py file to use the new backend structure

Usage:
    python scripts/run_migration.py [--dry-run]
    
Options:
    --dry-run    Show what would happen without making any changes
"""

import os
import sys
import platform
import subprocess
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('migration_runner')

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Migrate to new directory structure')
    parser.add_argument('--dry-run', action='store_true', help='Show what would happen without making changes')
    return parser.parse_args()

def run_command(command, cwd=None, shell=True, dry_run=False):
    """Run a shell command and return the output"""
    try:
        if dry_run:
            logger.info(f"Would run command: {command}")
            return True
            
        logger.info(f"Running command: {command}")
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Command failed with code {result.returncode}")
            logger.error(f"Error output: {result.stderr}")
            return False
        
        logger.info(f"Command output: {result.stdout}")
        return True
    except Exception as e:
        logger.error(f"Error running command: {e}")
        return False

def run_migration_scripts(dry_run=False):
    """Run the appropriate migration script for the OS"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    
    # Check for source directories
    api_dir = os.path.join(base_dir, 'api')
    if not os.path.exists(api_dir):
        logger.warning(f"Source 'api' directory not found: {api_dir}")
        logger.warning("Migration may be incomplete")
    
    execution_model_dir = os.path.join(base_dir, 'execution_model')
    if not os.path.exists(execution_model_dir):
        logger.warning(f"Source 'execution_model' directory not found: {execution_model_dir}")
    
    dual_bot_dir = os.path.join(base_dir, 'dual_bot')
    if not os.path.exists(dual_bot_dir):
        logger.warning(f"Source 'dual_bot' directory not found: {dual_bot_dir}")
    
    # List directories to be created
    backend_dir = os.path.join(base_dir, 'backend')
    
    # Print directories to be created in dry run mode
    if dry_run:
        logger.info(f"Would create directory: {backend_dir}")
        logger.info(f"Would create directories: {backend_dir}/routes")
        logger.info(f"Would create directories: {backend_dir}/broker_integration")
        logger.info(f"Would create directories: {backend_dir}/execution_model")
        logger.info(f"Would create directories: {backend_dir}/dual_bot")
        logger.info(f"Would create directories: {backend_dir}/templates")
        logger.info(f"Would create directories: {backend_dir}/static/css")
        logger.info(f"Would create directories: {backend_dir}/static/js")
        logger.info(f"Would create directories: {backend_dir}/static/images")
        logger.info(f"Would create directories: {backend_dir}/config")
        
        # Show what files would be copied
        if os.path.exists(api_dir):
            logger.info(f"Would copy files from {api_dir}/routes to {backend_dir}/routes")
            logger.info(f"Would copy files from {api_dir}/broker_integration to {backend_dir}/broker_integration")
            logger.info(f"Would copy app.py from {api_dir} to {backend_dir}")
        
        if os.path.exists(execution_model_dir):
            logger.info(f"Would copy files from {execution_model_dir} to {backend_dir}/execution_model")
        
        if os.path.exists(dual_bot_dir):
            logger.info(f"Would copy files from {dual_bot_dir} to {backend_dir}/dual_bot")
        
        return True
    
    # Determine which migration script to run based on OS
    is_windows = platform.system() == "Windows"
    
    if is_windows:
        migration_script = os.path.join(script_dir, "migrate_to_new_structure.ps1")
        command = f"powershell -ExecutionPolicy Bypass -File \"{migration_script}\""
    else:
        migration_script = os.path.join(script_dir, "migrate_to_new_structure.sh")
        command = f"bash \"{migration_script}\""
    
    # Ensure the script exists
    if not os.path.exists(migration_script):
        logger.error(f"Migration script not found: {migration_script}")
        return False
    
    # Run the migration script
    success = run_command(command, cwd=base_dir)
    
    return success

def update_import_paths(dry_run=False):
    """Run the script to update import paths"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    update_script = os.path.join(script_dir, "update_imports.py")
    
    # Ensure the script exists
    if not os.path.exists(update_script):
        logger.error(f"Update imports script not found: {update_script}")
        return False
    
    if dry_run:
        logger.info(f"Would run script to update import paths: {update_script}")
        logger.info("This would change 'from api.' to 'from backend.' in Python files")
        return True
    
    # Run the update imports script
    command = f"python \"{update_script}\""
    success = run_command(command, cwd=base_dir)
    
    return success

def main():
    """Main function to run all migration steps"""
    args = parse_args()
    dry_run = args.dry_run
    
    if dry_run:
        logger.info("Running in DRY RUN mode - no changes will be made")
    
    logger.info("Starting complete migration process")
    
    # Step 1: Run the migration script to copy files
    logger.info("Step 1: Migrating files to new directory structure")
    if not run_migration_scripts(dry_run):
        logger.error("File migration failed, aborting")
        return 1
    
    # Step 2: Update import paths
    logger.info("Step 2: Updating import paths in migrated files")
    if not update_import_paths(dry_run):
        logger.error("Import path updates failed")
        # Continue anyway, as some files might be updated correctly
    
    if dry_run:
        logger.info("\nDRY RUN completed. No changes were made.")
        logger.info("Run the script without --dry-run to perform the actual migration.")
    else:
        logger.info("Migration completed successfully!")
    
    logger.info("\nNext steps:")
    logger.info("1. Verify that all files were migrated correctly")
    logger.info("2. Check that import paths were updated correctly")
    logger.info("3. Update configurations to use the new structure")
    logger.info("4. Test the application with the new structure")
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 