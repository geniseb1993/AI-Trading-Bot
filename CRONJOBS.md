# AI Trading Bot - Cron Job Functionality

This document explains the automated cronjob features implemented for the AI Trading Bot.

## Overview

The AI Trading Bot includes a robust scheduling system that automates various tasks, including:

1. **Trading Cycles** - Execute trading operations at predetermined market hours
2. **Market Data Updates** - Fetch fresh market data at regular intervals
3. **Performance Reports** - Generate daily and weekly performance summaries
4. **Historical Data Cleanup** - Maintain system efficiency by cleaning old data
5. **System Health Checks** - Monitor the bot's health and automatically recover from issues

## Getting Started

### Prerequisites

Make sure you have the following dependencies installed:

```bash
npm install node-cron axios date-fns express
```

### Starting the Cron Scheduler

To start the cron scheduler, run:

```bash
node start-cron-server.js
```

This will start the cron job scheduler in the foreground with console output. You can also run it in the background using tools like PM2:

```bash
# Install PM2 if needed
npm install -g pm2

# Start the scheduler with PM2
pm2 start cron-scheduler.js --name "trading-bot-cron"
```

## Configuration

The cron scheduler's configuration is stored in `cron-config.json` and manages the following schedules:

| Task | Default Schedule | Description |
|------|-----------------|-------------|
| Market Data Update | Every 15 minutes during market hours | Fetches latest market data for tracked symbols |
| Morning Trading Cycle | 9:30 AM ET, Mon-Fri | Executes main morning trading strategy |
| Evening Trading Cycle | 3:00 PM ET, Mon-Fri | Executes main evening trading strategy |
| Additional Trading Cycles | 11:00 AM ET, 1:00 PM ET, Mon-Fri | Additional intraday trading cycles |
| Daily Report | 5:00 PM ET, Mon-Fri | Generates daily performance summary |
| Weekly Report | 6:00 PM ET, Friday | Generates weekly performance summary |
| Data Cleanup | 2:00 AM ET, Sunday | Cleans up old logs and reports |
| System Health Check | Every 30 minutes | Monitors system health and auto-recovers |

### Custom Configuration

You can modify these schedules by editing the `cron-config.json` file. The scheduler will automatically reload your configuration.

Alternatively, you can use the scheduler's REST API to update settings:

```bash
# Example: Update market data interval
curl -X POST http://localhost:5050/config \
  -H "Content-Type: application/json" \
  -d '{"marketDataInterval": 10}'
```

## REST API

The scheduler exposes a simple REST API on port 5050 (configurable via CRON_PORT environment variable):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/status` | GET | Get current scheduler status and configuration |
| `/config` | POST | Update scheduler configuration |
| `/run/:task` | POST | Manually trigger a specific task |

## Task Details

### Market Data Collection

This task fetches the latest market data for all symbols configured in your market data settings. It only runs during market hours (9:00 AM - 4:00 PM ET, Monday-Friday).

### Trading Cycles

Trading cycles execute the bot's trading strategy at strategic times:
- **Morning cycle (9:30 AM)**: Initial position setup and early market response
- **Mid-day cycles (11:00 AM, 1:00 PM)**: Adjustment based on intraday movements
- **Evening cycle (3:00 PM)**: Final position adjustments before market close

These cycles only run if the bot is in "active" status.

### Performance Reports

- **Daily reports**: Generate end-of-day summaries with performance metrics and active trades
- **Weekly reports**: Provide broader performance trends and statistics

Reports are saved to the `logs` directory in JSON format.

### System Maintenance

- **Data cleanup**: Removes logs and reports older than 30 days
- **Health checks**: Monitors API server and bot status, attempting recovery when needed

## Logs

Cron job logs are stored in the `logs` directory with the filename format `cron-YYYY-MM-DD.log`.

## Troubleshooting

If you encounter issues with the scheduler:

1. Check the logs in the `logs` directory
2. Verify the API server is running and accessible
3. Ensure the correct permissions for log file creation
4. Check that all required dependencies are installed

## Integration with Trading Bot

The cron scheduler integrates with the existing trading bot by making API calls to the bot's REST endpoints. This non-invasive approach ensures that the scheduler operates independently from the main application logic.

The bot's autonomous features continue to function as designed, with the scheduler simply triggering operations at the appropriate times.

## Security Considerations

The cron scheduler's API does not implement authentication in this version. For production deployment, consider:

1. Adding API key authentication
2. Restricting access to the scheduler's API port
3. Using HTTPS for all API communications
4. Running the scheduler with limited system permissions 