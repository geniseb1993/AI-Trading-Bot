# Deploying AI Trading Bot to Render

This guide provides step-by-step instructions for deploying the AI Trading Bot API to Render.com.

## Prerequisites

1. A [Render account](https://render.com/)
2. Your project code pushed to GitHub or GitLab

## Automatic Deployment

The easiest way to deploy is using the render.yaml configuration file:

1. Log in to your Render account
2. Go to the Dashboard
3. Click on "New" and select "Blueprint"
4. Connect your GitHub/GitLab account if not already connected
5. Select the AI Trading Bot repository
6. Render will automatically detect the render.yaml file and set up your services
7. Configure your environment variables in the Render dashboard
8. Click "Apply"

## Manual Deployment

If you prefer to set up your service manually:

### 1. Log in to Render

Go to [Render Dashboard](https://dashboard.render.com/) and log in.

### 2. Create a New Web Service

- Click "New" and select "Web Service"
- Connect your GitHub/GitLab repository
- Select the repository containing the AI Trading Bot code
- Give your service a name (e.g., "ai-trading-bot-api")

### 3. Configure Settings

Use the following configuration:
- **Environment**: Python
- **Region**: Choose the region closest to your users
- **Branch**: main (or your preferred branch)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python ensure_directories.py && gunicorn wsgi:app --workers=4 --threads=2 --timeout=120 --bind=0.0.0.0:$PORT`

### 4. Set Environment Variables

Click on "Environment" and add the following variables:
- `PYTHON_VERSION`: 3.9.0
- `FLASK_ENV`: production
- `FLASK_DEBUG`: 0

And add your secret API keys:
- `OPENAI_API_KEY`: Your OpenAI API key
- `ALPACA_API_KEY`: Your Alpaca API key
- `ALPACA_SECRET_KEY`: Your Alpaca secret key
- `POLYGON_API_KEY`: Your Polygon API key
- `NEWS_API_KEY`: Your News API key
- `DISCORD_WEBHOOK_URL`: Your Discord webhook URL
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID

### 5. Configure Additional Options

- **Plan**: Select a plan that fits your needs (Free tier is fine for testing)
- **Health Check Path**: `/api/health`
- **Auto-Deploy**: Enable (if you want automatic deployments on git push)

### 6. Create Disk Storage (Optional)

If you need persistent storage for data:
1. Go to your web service dashboard
2. Click on "Disks" on the left sidebar
3. Click "Create Disk"
4. Set mount path to `/data`
5. Choose an appropriate size (1GB minimum)

## Post-Deployment

After your deployment is complete:

1. Check the logs to make sure everything started correctly
2. Visit your application URL to verify it's working
3. Test the API endpoints using tools like Postman or curl

Example test:
```bash
curl https://your-app-name.onrender.com/api/health
```

## Troubleshooting

If you encounter issues:

1. Check the logs in the Render dashboard
2. Verify all environment variables are set correctly
3. Ensure all required directories are created by the ensure_directories.py script
4. Make sure the API keys you've provided are valid

## Updating Your Deployment

When you make changes to your code:

1. Push your changes to your GitHub/GitLab repository
2. Render will automatically rebuild and deploy if auto-deploy is enabled
3. Monitor the deployment logs for any build or runtime errors

## Cost Optimization

- The free tier of Render has limitations and will spin down after periods of inactivity
- For production use, consider at least the "Starter" plan ($7/mo) to keep your service always running
- You can scale up resources as needed in the Render dashboard

# Render Deployment Fix Summary

This document outlines the changes made to fix deployment issues on the Render platform.

## Issues Fixed

1. **Missing `alpaca-trade-api` Package**
   - Added `alpaca-trade-api==3.2.0` to `requirements.txt`
   - Created a simplified mock implementation in `mock_modules/alpaca_trade_api.py` that doesn't require pandas or numpy

2. **Configuration Files Not Found**
   - Created `config.json` with default values
   - Created `broker_config.json` with default values
   - Created `execution_model_config.json` with default values
   - Created `config/environments/market_data_config.json` with default values
   - Developed `copy_config_files.py` to ensure all config files are properly placed

3. **'int' object has no attribute 'get' Error in WSGI Initialization**
   - Modified `wsgi.py` to properly handle the PORT environment variable
   - Added early PORT variable conversion and validation
   - Added better error handling for PORT value processing

4. **CSS Directory Structure Issues**
   - Fixed static folder configuration in `render.yaml`
   - Created necessary subdirectories (`static/css`, `static/js`, etc.)
   - Added explicit route handlers for CSS and JS files
   - Fixed path issues for CSS imports in the frontend

5. **Missing Directories**
   - Added directory creation code in `wsgi.py` and `copy_config_files.py`
   - Ensured all required directories exist before app initialization

## Files Modified/Created

1. **Modified Files**
   - `requirements.txt` - Added alpaca-trade-api dependency
   - `render.yaml` - Updated build and start commands
   - `wsgi.py` - Fixed PORT handling and added directory creation

2. **Created Files**
   - `mock_modules/alpaca_trade_api.py` - Simple mock implementation
   - `config.json` - Default application configuration
   - `broker_config.json` - Default broker configuration
   - `execution_model_config.json` - Default execution model configuration
   - `copy_config_files.py` - Script to copy config files to required locations
   - `verify_render_deployment.py` - Script to verify deployment fixes
   - `.render/build.yaml` - Build configuration for Render

## Verification

To verify these fixes are working correctly, you can run:

```bash
python verify_render_deployment.py
```

This script will check:
- All required directories exist
- All configuration files exist and are valid
- The alpaca-trade-api package is available (either real or mock)
- The wsgi.py file has the proper PORT handling
- All environment variables are properly set

## Additional Notes

- The mock alpaca_trade_api implementation provides a simplified interface that doesn't require pandas or numpy
- All configuration files use sensible defaults for a mock/simulation environment
- The application is configured to use mock implementations when running on Render
- Static file handling includes fallbacks to ensure CSS and JavaScript are properly served 