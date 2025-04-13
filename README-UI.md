# AI Trading Bot - Enhanced UI

This repository contains the enhanced UI for the AI Trading Bot, featuring a modern, futuristic React frontend and a Flask API backend.

## Overview

The enhanced version maintains all the core functionality of the original AI Trading Bot but adds:

- A modern React-based web interface with a futuristic design
- RESTful API to interact with the trading bot's core functionality
- Interactive charts and visualizations
- Real-time signal monitoring
- Advanced settings management
- Secure Vault Authentication system

## Recent Enhancements (2025-04-02)

### Vault Authentication System
- **PIN-Based Security**: Secure 4-digit PIN authentication (8080) protects your trading data
- **Automatic Validation**: PIN is validated as soon as 4 digits are entered, no submit button needed
- **Cyberpunk UI**: Futuristic interface with animated elements, glowing effects, and digital readout
- **Audio Feedback**: Sound effects for successful and failed authentication attempts
- **Visual Feedback**: Color changes and animations provide clear status updates
- **Session Persistence**: Authentication state is remembered across browser sessions
- **Logout Functionality**: "Close Vault" button to secure the application when not in use

### Audio Integration
- **Custom Sound Effects**:
  - Access Granted: `access-granted-87075.mp3` plays on successful login
  - Access Denied: `access-denied-101308.mp3` plays when incorrect PIN is entered
- **Diagnostic Tools**: Added `/audio-test.html` and `/sounds/debug.html` for troubleshooting
- **Robust Error Handling**: Multiple fallback mechanisms for audio playback

### UI Improvements
- Fixed undefined variables in React components
- Resolved missing file errors
- Addressed ESLint warnings
- Enhanced error handling throughout the application
- Implemented fallback data for API connection issues

## Project Structure

```
ai-trading-bot/
├── api/                # Flask API backend
│   └── app.py          # API endpoints
├── frontend/           # React frontend
│   ├── public/         # Static files
│   │   └── sounds/     # Audio files for the Vault system
│   └── src/            # React source code
│       ├── components/ # Reusable components
│       │   └── VaultAuth.js  # Vault Authentication component
│       ├── pages/      # Page components
│       ├── utils/      # Utility functions
│       └── assets/     # Images, icons, etc.
└── [original files]    # Original trading bot Python files
```

## Installation

### Prerequisites

- Python 3.7+
- Node.js 14+ and npm

### Backend Setup

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Start the Flask API server:

```bash
cd api
python app.py
```

The API will be available at `http://localhost:5000`.

### Frontend Setup

1. Install npm dependencies:

```bash
cd frontend
npm install
```

2. Set up audio files for the Vault authentication:

```bash
npm run setup-audio
```

3. Start the development server:

```bash
npm start
```

The web interface will be available at `http://localhost:3000`.

## Usage

### Vault Authentication

On first launch, you'll be presented with the Vault Authentication screen:

1. Enter the 4-digit PIN: `8080`
2. The PIN will be automatically validated when all 4 digits are entered
3. Upon successful authentication, you'll hear a confirmation sound and be redirected to the dashboard
4. To log out, click the "Close Vault" button in the top right corner of the application

### Dashboard

The dashboard provides a quick overview of:
- Current trading signals
- Performance metrics
- Active trades
- Market trends

### Signals

The Signals page allows you to:
- View and filter current buy/sell signals
- Generate new signals
- Customize signal parameters

### Backtest

The Backtest page enables you to:
- Run backtests on historical data
- Visualize performance metrics
- Analyze trade history
- Optimize trading strategies

### Settings

The Settings page allows you to configure:
- Trading parameters
- Signal thresholds
- User interface preferences
- API connections

## Troubleshooting

### Audio Issues

If you experience issues with sound effects:

1. Visit `http://localhost:3000/audio-test.html` to run diagnostics
2. Check that your browser supports audio playback
3. Verify that sound files exist in the `public/sounds` directory
4. Ensure your system volume is turned up

## Technologies Used

- **Backend**: Python, Flask, Pandas, NumPy
- **Frontend**: React, Material-UI, Nivo Charts, Framer Motion
- **Data Visualization**: Recharts, Nivo
- **Authentication**: Custom Vault system with localStorage persistence
- **Audio**: Web Audio API with fallback mechanisms

## Original Documentation

The original AI Trading Bot documentation is still applicable for core functionality:
- See the original README.md for details on the trading algorithms
- Refer to CHANGELOG.md for version history 