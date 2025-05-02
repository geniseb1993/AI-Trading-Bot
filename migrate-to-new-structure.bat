@echo off
echo Starting migration to new directory structure...
echo This will reorganize the project to follow the standardized layout.
echo.

set DRY_RUN=0
if "%1"=="--dry-run" set DRY_RUN=1
if "%1"=="-d" set DRY_RUN=1

if %DRY_RUN%==1 (
    echo [DRY RUN MODE] No changes will be made. This will show what would happen.
) else (
    echo Files will be copied from the old structure to the new one.
    echo No files will be deleted from the original structure.
    echo.
    choice /M "Do you want to continue with the migration"
    if errorlevel 2 (
        echo Migration cancelled.
        exit /b
    )
)

echo.
echo Running Python migration script...
if %DRY_RUN%==1 (
    python scripts\run_migration.py --dry-run
) else (
    python scripts\run_migration.py
)

echo.
if %DRY_RUN%==1 (
    echo Dry run completed! No changes were made.
    echo To perform the actual migration, run this script without the --dry-run option.
) else (
    echo Migration process completed!
)
echo.
echo Next steps:
echo 1. Verify that all files were migrated correctly
echo 2. Update any configurations to use the new structure
echo 3. Test the application to ensure everything works correctly
echo.
pause 