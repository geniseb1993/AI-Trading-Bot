# Migration script to move files from the old structure to the new directory layout
# This script moves route files and other components from api/ to backend/

# Create function to migrate files with proper error handling
function Migrate-Files {
    param (
        [string]$sourceDir,
        [string]$targetDir,
        [string]$description
    )
    
    Write-Host "Migrating $description from $sourceDir to $targetDir..." -ForegroundColor Cyan
    
    # Create target directory if it doesn't exist
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        Write-Host "  Created directory: $targetDir" -ForegroundColor Green
    }
    
    # Check if source directory exists
    if (-not (Test-Path $sourceDir)) {
        Write-Host "  WARNING: Source directory $sourceDir does not exist, skipping..." -ForegroundColor Yellow
        return
    }
    
    # Copy files from source to target
    $files = Get-ChildItem -Path $sourceDir -File
    foreach ($file in $files) {
        $targetFile = Join-Path -Path $targetDir -ChildPath $file.Name
        
        # Don't overwrite existing files unless forced
        if (Test-Path $targetFile) {
            Write-Host "  File already exists (not overwriting): $targetFile" -ForegroundColor Yellow
        } else {
            Copy-Item -Path $file.FullName -Destination $targetFile
            Write-Host "  Copied: $($file.Name)" -ForegroundColor Green
        }
    }
    
    # Copy subdirectories recursively
    $dirs = Get-ChildItem -Path $sourceDir -Directory
    foreach ($dir in $dirs) {
        $sourceSubDir = Join-Path -Path $sourceDir -ChildPath $dir.Name
        $targetSubDir = Join-Path -Path $targetDir -ChildPath $dir.Name
        
        Migrate-Files -sourceDir $sourceSubDir -targetDir $targetSubDir -description "$description/$($dir.Name)"
    }
}

# Main migration process
Write-Host "Starting migration to new directory structure..." -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# 1. Migrate route files
Migrate-Files -sourceDir "api/routes" -targetDir "backend/routes" -description "route files"

# 2. Migrate broker integration files
Migrate-Files -sourceDir "api/broker_integration" -targetDir "backend/broker_integration" -description "broker integration files"

# 3. Migrate execution model files
Migrate-Files -sourceDir "execution_model" -targetDir "backend/execution_model" -description "execution model files"

# 4. Migrate dual bot files
Migrate-Files -sourceDir "dual_bot" -targetDir "backend/dual_bot" -description "dual bot files"

# 5. Migrate lib files
Migrate-Files -sourceDir "api/lib" -targetDir "backend/lib" -description "library files"

# 6. Migrate middleware files
Migrate-Files -sourceDir "api/middleware" -targetDir "backend/middleware" -description "middleware files"

# 7. Migrate utility files
Migrate-Files -sourceDir "api/utils" -targetDir "backend/utils" -description "utility files"

# 8. Migrate template files
Migrate-Files -sourceDir "api/templates" -targetDir "backend/templates" -description "template files"

# 9. Migrate static files if needed
Migrate-Files -sourceDir "api/static" -targetDir "backend/static" -description "static files"

Write-Host "Migration completed successfully!" -ForegroundColor Green
Write-Host "Please check the migrated files to ensure everything is in the correct location." -ForegroundColor Cyan
Write-Host "You may need to update import paths in the migrated files." -ForegroundColor Yellow 