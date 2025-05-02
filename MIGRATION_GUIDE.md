# Migration Guide: Standardizing the Directory Structure

This guide explains the process of migrating the AI Trading Bot V2.0 project from its original directory structure to a more standardized layout that follows modern best practices and is compatible with deployment platforms like Render.

## Why Migrate?

The new directory structure offers several benefits:

1. **Better organization**: Clearer separation of concerns between frontend, backend, and other components
2. **Standardized layout**: Follows common conventions for Flask/React applications
3. **Improved deployment**: More compatible with platforms like Render
4. **Enhanced maintainability**: Easier to find and modify code
5. **Better scalability**: Makes it simpler to add new features or components

## Directory Structure Changes

### Original Structure

The original structure had several issues:
- API code was spread across multiple directories
- Inconsistent naming conventions
- Unclear boundaries between components
- Difficult deployment configuration

### New Structure

The new standardized structure follows this layout:

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
├── data/                               # Data storage
│   ├── broker/
│   ├── market_data/
│   ├── signals/
│   └── logs/
│
├── tests/                              # Test suite
│   ├── __init__.py
│   └── test_routes.py
│
├── scripts/                            # Utility scripts
│   ├── render_fix.py
│   └── utilities/
│
├── config/                             # Configuration
│   ├── environments/
│   └── secrets/
│
├── .env                                # Environment variables
├── .gitignore
├── requirements.txt                    # Python dependencies
├── wsgi.py                             # WSGI entry point
└── render.yaml                         # Render deploy config
```

## Migration Process

### Automated Migration

We've provided scripts to automate most of the migration process:

#### For Windows Users

Run the batch file:
```
migrate-to-new-structure.bat
```

#### For macOS/Linux Users

Run the shell script:
```
bash migrate-to-new-structure.sh
```

#### What the Scripts Do

1. Copy files from their original locations to the new directory structure
2. Update import paths in the migrated files (changing 'api.' to 'backend.')
3. Create any missing directories in the new structure

### Manual Steps After Migration

After running the migration scripts, you may need to:

1. **Verify file imports**: Some import statements might need manual updates
2. **Update configurations**: Make sure any config files point to the correct locations
3. **Check for hardcoded paths**: Update any hardcoded paths to use the new structure
4. **Test the application**: Ensure everything works correctly with the new structure

## Running the Application with the New Structure

### Starting the Flask Backend

```bash
python -m backend.app
```

Or using Gunicorn:
```bash
gunicorn wsgi:app
```

### Running Tests

```bash
python -m unittest discover tests
```

## Deployment

The application is now configured for easy deployment on Render using the `render.yaml` file. Simply connect your GitHub repository to Render and it will automatically deploy the application.

## Troubleshooting

### Common Issues

1. **Import errors**: If you see import errors, check that the paths are correctly updated. You may need to run the `scripts/update_imports.py` script again or fix some imports manually.

2. **File not found errors**: Make sure all files were copied correctly to the new structure.

3. **Configuration issues**: Check that any configuration files point to the correct locations.

### Still Having Problems?

If you encounter issues during or after migration:

1. Check the migration logs in the console output
2. Compare the old and new structures to ensure all files were copied correctly
3. Review import statements in the files that cause errors

## Reverting the Migration

Since the migration script only copies files without deleting the originals, you can revert to the old structure by:

1. Using the original paths in your code
2. Updating any changes made to configuration files

## Questions and Support

If you have questions or need support with the migration process, please create an issue in the GitHub repository. 