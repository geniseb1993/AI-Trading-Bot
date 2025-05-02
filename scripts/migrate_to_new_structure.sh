#!/bin/bash
# Migration script to move files from the old structure to the new directory layout
# This script moves route files and other components from api/ to backend/

# ANSI color codes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Create function to migrate files with proper error handling
migrate_files() {
    local sourceDir=$1
    local targetDir=$2
    local description=$3
    
    echo -e "${CYAN}Migrating $description from $sourceDir to $targetDir...${NC}"
    
    # Create target directory if it doesn't exist
    if [ ! -d "$targetDir" ]; then
        mkdir -p "$targetDir"
        echo -e "${GREEN}  Created directory: $targetDir${NC}"
    fi
    
    # Check if source directory exists
    if [ ! -d "$sourceDir" ]; then
        echo -e "${YELLOW}  WARNING: Source directory $sourceDir does not exist, skipping...${NC}"
        return
    fi
    
    # Copy files from source to target (non-recursive, just this directory)
    for file in "$sourceDir"/*; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            targetFile="$targetDir/$filename"
            
            # Don't overwrite existing files unless forced
            if [ -f "$targetFile" ]; then
                echo -e "${YELLOW}  File already exists (not overwriting): $targetFile${NC}"
            else
                cp "$file" "$targetFile"
                echo -e "${GREEN}  Copied: $filename${NC}"
            fi
        fi
    done
    
    # Process subdirectories recursively
    for dir in "$sourceDir"/*/; do
        if [ -d "$dir" ]; then
            dirName=$(basename "$dir")
            sourceSubDir="$sourceDir/$dirName"
            targetSubDir="$targetDir/$dirName"
            
            migrate_files "$sourceSubDir" "$targetSubDir" "$description/$dirName"
        fi
    done
}

# Main migration process
echo -e "${CYAN}Starting migration to new directory structure...${NC}"
echo -e "${CYAN}=================================================${NC}"

# 1. Migrate route files
migrate_files "api/routes" "backend/routes" "route files"

# 2. Migrate broker integration files
migrate_files "api/broker_integration" "backend/broker_integration" "broker integration files"

# 3. Migrate execution model files
migrate_files "execution_model" "backend/execution_model" "execution model files"

# 4. Migrate dual bot files
migrate_files "dual_bot" "backend/dual_bot" "dual bot files"

# 5. Migrate lib files
migrate_files "api/lib" "backend/lib" "library files"

# 6. Migrate middleware files
migrate_files "api/middleware" "backend/middleware" "middleware files"

# 7. Migrate utility files
migrate_files "api/utils" "backend/utils" "utility files"

# 8. Migrate template files
migrate_files "api/templates" "backend/templates" "template files"

# 9. Migrate static files if needed
migrate_files "api/static" "backend/static" "static files"

echo -e "${GREEN}Migration completed successfully!${NC}"
echo -e "${CYAN}Please check the migrated files to ensure everything is in the correct location.${NC}"
echo -e "${YELLOW}You may need to update import paths in the migrated files.${NC}" 