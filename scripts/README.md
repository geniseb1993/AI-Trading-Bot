# Migration Scripts

This directory contains scripts to help with migrating the project from the original structure to the new, more standardized directory structure.

## Scripts

### migrate_to_new_structure.ps1

PowerShell script to migrate files from the old structure to the new directory layout. This script is for Windows users.

Usage:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\migrate_to_new_structure.ps1
```

### migrate_to_new_structure.sh

Bash script to migrate files from the old structure to the new directory layout. This script is for macOS/Linux users.

Usage:
```bash
bash scripts/migrate_to_new_structure.sh
```

### update_imports.py

Python script to update import paths in the migrated files from 'api.' to 'backend.'

Usage:
```bash
python scripts/update_imports.py
```

### run_migration.py

A comprehensive script that runs all migration steps in sequence. This is the recommended way to run the migration.

Usage:
```bash
python scripts/run_migration.py
```

## Migration Process

The migration process involves:

1. Copying files from the old structure to the new directory layout
2. Updating import paths in the migrated files
3. Testing the application with the new structure

After migration, the directory structure should look like:

```
AI-Trading-Bot-V2.0/
│
├── backend/                            # Flask backend
│   ├── __init__.py
│   ├── app.py                          # Flask entry point
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── bot_routes.py
│   │   ├── health_routes.py
│   │   └── dashboard_routes.py
│   ├── broker_integration/
│   │   ├── __init__.py
│   │   ├── alpaca_broker.py
│   │   └── mock_broker.py
│   ├── execution_model/
│   │   └── execution_logic.py
│   ├── dual_bot/
│   │   └── controller.py
│   ├── templates/
│   │   └── index.html
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── config/
│       ├── __init__.py
│       └── settings.py
│
├── frontend/                           # React frontend
│   ├── public/
│   ├── src/
│   ├── package.json
│
├── ... (other directories)
```

## Notes

- The migration scripts do not delete any files from the original structure
- You may need to manually fix some imports or configurations after migration
- Always test the application after migration to ensure everything works correctly
