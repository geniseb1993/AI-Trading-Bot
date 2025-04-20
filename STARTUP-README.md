# AI Trading Bot V2.0 - Unified Startup Guide

This document describes the unified startup process for the AI Trading Bot V2.0 application, which addresses previous signal generation inconsistencies and startup script complexities.

## New Unified Startup Process

The application now has a single, reliable entry point:

- **Windows**: Run `start-app.bat`
- **Linux/Mac**: Run `./start-app.sh` (make sure to `chmod +x start-app.sh` first)

These scripts execute the `app-starter.py` file, which handles:

1. Environment setup and validation
2. Signal generation with robust error handling
3. Starting both backend API server and frontend React app
4. Health checks to ensure all components are running

## Signal Generation Improvements

The new implementation addresses previous signal generation issues by:

1. **Using deterministic signal generation**: Signals are now consistently generated with the same score for a symbol, eliminating random fluctuations between restarts.

2. **Robust error handling**: The system gracefully falls back to synthetic data generation if API access fails, maintaining consistent signal quality.

3. **Consolidated logic**: All signal generation is now handled in one place instead of across multiple scripts.

4. **Real data prioritization**: The system attempts to use real market data from Alpaca first and only falls back to synthetic data when necessary.

## File Structure Changes

- **app-starter.py**: The new centralized application starter that replaces multiple legacy startup scripts
- **start-app.bat/start-app.sh**: Simple convenience wrappers for different operating systems

## Legacy Scripts (Do Not Use)

The following scripts are deprecated and should no longer be used:

- `start-all.bat`
- `run-server.bat`
- `run-minimal.bat`
- `run-api-direct.bat`
- `run-api-server.bat`
- `start-servers.js`
- `start-servers.bat`
- `start-servers.ps1`

## Troubleshooting

If you encounter issues:

1. Check the logs in `data/logs/app-starter.log` for detailed information
2. Ensure all required packages are installed: `pip install -r requirements.txt`
3. Verify your `.env` file contains the necessary API credentials
4. Make sure ports 3000 (frontend) and 5000 (backend) are available

## For Developers

If you need to modify the startup process:

1. Edit `app-starter.py` directly, following the existing modular structure
2. Each major function has clear documentation and error handling
3. The script is designed to be maintainable and expandable for future features 