"""
Script to create a secure backup of the .env file.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

def backup_env():
    # Source .env file path
    source_env = Path("C:/Users/davis/OneDrive/Documents/GitHub/AI-Trading-Bot V2.0/.env")
    
    # Create backups directory if it doesn't exist
    backup_dir = Path("secure_backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f".env.backup_{timestamp}"
    
    try:
        # Copy the .env file to the backup location
        shutil.copy2(source_env, backup_file)
        print(f"Successfully created backup at: {backup_file}")
        print("Please store this backup in a secure location outside of the project directory.")
        
    except Exception as e:
        print(f"Error creating backup: {str(e)}")
        print("Please ensure you have the correct permissions and the source file exists.")

if __name__ == "__main__":
    backup_env() 