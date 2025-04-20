# Dual Bot Trading System

A modular, semi-automated trading system designed for high-performance scalping and momentum strategies, specifically 0DTE options on QQQ, TSLA, and PLTR.

## Features

- **0DTE Scanner**: Targets 80% win rate setups (SPX/QQQ)
- **Pre-Market Gapper Alerts**: Finds morning momentum plays
- **Dark Pool Radar**: Flags hidden institutional moves
- **CEO Dashboard**: Your "command center"
- **Auto-Closer**: Locks in profits/stops (Alpaca)
- **ChatGPT Risk Manager**: Provides risk assessments for trade recommendations

## System Architecture

```
flowchart TB
    subgraph Data_Layer
        A[Unusual Whales] -->|Flow Data| B[DeepSeek]
        C[Polygon WS] -->|Real-time Ticks| B
        D[NewsAPI] -->|Fed/Earnings| E[ChatGPT]
    end

    subgraph AI_Core
        B -->|"Top 3 Trades/Day"| F[CEO Dashboard]
        B -->|Risk Limits| G[Auto-Closer]
        E -->|"1-Line Risk Summary"| F
    end

    subgraph Execution
        F -->|"Approve/Reject"| H[Schwab Manual Entry]
        G -->|"Close at Target/Stop"| I[Alpaca]
    end
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/dual-bot.git
   cd dual-bot
   ```

2. Install the required dependencies:
   ```
   pip install -r dual_bot/requirements.txt
   ```

3. Set up the configuration:
   ```
   python dual_bot/setup_config.py
   ```

## Configuration

The Dual Bot requires several API keys to function properly:

- **Polygon.io**: For market data
- **Unusual Whales**: For flow data
- **News API**: For news data
- **DeepSeek**: For trade recommendations
- **OpenAI**: For risk management
- **Alpaca**: For automated trade execution

You can configure these API keys using the setup script:

```
python dual_bot/setup_config.py
```

## Usage

### Running the Bot

To run the Dual Bot:

```
python dual_bot/run_bot.py
```

### Testing the Bot

To test the functionality of the Dual Bot:

```
python dual_bot/test_bot.py
```

### CEO Ritual (5 min/day)

- 9:00 AM: Review DeepSeek's top 3 trades
- 9:05 AM: Read ChatGPT veto
- 9:10 AM: Enter trade in Schwab **only if**:
  - ChatGPT = YES
  - Your gut agrees (CEO override power)

## Components

### DeepSeek Scanner

The DeepSeek Scanner analyzes market data to identify high-probability trading opportunities. It uses the DeepSeek AI model to generate trade recommendations based on technical analysis, market sentiment, and flow data.

### ChatGPT Risk Manager

The ChatGPT Risk Manager assesses trade recommendations and provides risk assessments. It uses the OpenAI API to analyze trade recommendations based on market context and signals.

### Auto-Closer

The Auto-Closer automatically closes trades at predefined targets or stops. It monitors active positions and executes orders through the Alpaca API when exit conditions are met.

### Data Fetcher

The Data Fetcher retrieves market data, options data, and news data from various sources, including Polygon.io, Unusual Whales, and News API.

## Logging

Logs are stored in the `dual_bot/logs` directory. The log level can be configured in the `config.json` file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Do not use it for actual trading without understanding the risks involved. The authors are not responsible for any financial losses incurred from using this software. 