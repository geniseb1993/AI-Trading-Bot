#!/bin/bash

# ANSI color codes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${CYAN}Starting migration to new directory structure...${NC}"
echo -e "This will reorganize the project to follow the standardized layout."
echo ""

# Check for dry run flag
DRY_RUN=0
if [ "$1" == "--dry-run" ] || [ "$1" == "-d" ]; then
    DRY_RUN=1
    echo -e "${YELLOW}[DRY RUN MODE] No changes will be made. This will show what would happen.${NC}"
else
    echo -e "Files will be copied from the old structure to the new one."
    echo -e "${YELLOW}No files will be deleted from the original structure.${NC}"
    echo ""
    read -p "Do you want to continue with the migration? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Migration cancelled.${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${CYAN}Running Python migration script...${NC}"
if [ $DRY_RUN -eq 1 ]; then
    python scripts/run_migration.py --dry-run
else
    python scripts/run_migration.py
fi

echo ""
if [ $DRY_RUN -eq 1 ]; then
    echo -e "${YELLOW}Dry run completed! No changes were made.${NC}"
    echo -e "To perform the actual migration, run this script without the --dry-run option."
else
    echo -e "${GREEN}Migration process completed!${NC}"
fi
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo -e "1. Verify that all files were migrated correctly"
echo -e "2. Update any configurations to use the new structure"
echo -e "3. Test the application to ensure everything works correctly"
echo ""
read -p "Press Enter to exit..." 