# AI Signal Ranking System

## Overview

The AI Signal Ranking system enhances trading decisions by applying machine learning and AI to trade signals. It ranks potential trades based on historical performance, technical factors, and market conditions. Additionally, it leverages GPT-powered insights to provide detailed market analysis and optimize trade parameters.

## Features

- **ML-based Signal Ranking**: Ranks trade signals based on multiple factors including volume, trend strength, and historical performance
- **Confidence Scoring**: Assigns confidence scores to help prioritize the most promising signals
- **GPT-powered Market Analysis**: Provides in-depth market analysis and trading insights from advanced language models
- **Trade Setup Optimization**: Enhances trade parameters like stop loss and take profit levels based on AI insights
- **Market Summaries**: Generates broad market condition analysis to inform overall strategy

## Signal Ranking Factors

The system scores signals based on several key factors:

| Factor | Description | Weight |
|--------|-------------|--------|
| Volume Ratio | Recent volume compared to baseline | 25% |
| Trend Strength | Price momentum and direction | 25% |
| Historical Win Rate | Past performance for symbol/setup | 30% |
| Institutional Flow | Smart money indicators | 20% |

## Installation Requirements

To use the AI Signal Ranking system with GPT-powered insights, you need:

1. An [OpenRouter](https://openrouter.ai/) API key (added to .env file as `OPENROUTER_API_KEY`)
2. Required Python packages:
   - pandas
   - numpy
   - openai
   - python-dotenv

## Usage

### Configuration

Configure the AI Signal Ranking system in the `config.py` file under the `ai_signal_ranking` section:

```python
"ai_signal_ranking": {
    "enabled": True,
    "min_confidence_threshold": 0.65,  # Minimum AI confidence to consider a signal valid
    "volume_weight": 0.25,            # Weight for volume factor in ranking
    "trend_weight": 0.25,             # Weight for trend strength in ranking
    "historical_weight": 0.30,        # Weight for historical performance in ranking
    "institutional_weight": 0.20,     # Weight for institutional flow in ranking
    "use_gpt_insights": True,         # Whether to use GPT for market analysis
    "gpt_model": "anthropic/claude-3.7-sonnet",  # Default GPT model to use
    "insights_cache_minutes": 60,     # How long to cache GPT insights 
    "insights_symbols_per_day": 10,   # How many symbols to analyze per day (API cost control)
    "daily_market_summary": True,     # Whether to generate daily market summaries
    "optimize_trade_setups": True,    # Whether to enhance trade setups with GPT insights
    "confidence_boost_threshold": 0.8  # AI confidence above which position size can be increased
}
```

### Basic Usage

The AI Signal Ranking module is automatically integrated with the ExecutionAlgorithm class. When a trade signal is received, it is ranked using the following process:

1. Signals are scored across multiple factors
2. Confidence score is calculated using weighted factors
3. Signals below the confidence threshold are filtered out
4. Top signals are optimized with GPT insights (if enabled)
5. Position size may be adjusted based on confidence level

### Example Code

```python
from execution_model.ai_signal_ranking import AISignalRanking
from execution_model.config import get_config
from execution_model.pnl_logger import PnLLogger

# Initialize components
config = get_config()
pnl_logger = PnLLogger(config)
ai_ranking = AISignalRanking(config, pnl_logger)

# Rank signals
ranked_signals = ai_ranking.rank_signals(signals, market_data)

# Get GPT insights for a specific symbol
insights = ai_ranking.get_gpt_insights([symbol], market_data)

# Optimize a trade setup
optimized_setup = ai_ranking.optimize_trade_setup(trade_setup, symbol_data)

# Get overall market summary
market_summary = ai_ranking.get_market_summary(market_data)
```

## GPT-Powered Insights

The system can provide detailed insights for trading decisions, including:

- **Market Conditions**: Current market state and trend direction
- **Support/Resistance Levels**: Key price levels to watch
- **Setup Quality Rating**: 1-10 rating of the current setup
- **Risk Analysis**: Specific risks to be aware of
- **Directional Bias**: Clear market direction (bullish, bearish, neutral)
- **Entry/Exit Points**: Optimal entry points and exit targets
- **Stop Loss Guidance**: Suggested stop loss levels based on technical analysis

## Testing

You can test the AI Signal Ranking functionality using the provided test script:

```bash
python test_ai_ranking.py
```

This will generate sample signals and market data, demonstrate the ranking process, and test the GPT-powered insights.

## Integration with Execution Algorithm

The AI Signal Ranking system is automatically integrated with the ExecutionAlgorithm. When enabled, it:

1. Ranks incoming trade signals
2. Filters out low-confidence signals
3. Optimizes parameters for high-quality setups
4. Can increase position size for high-confidence signals
5. Provides additional context through GPT insights

## Performance Impact

- **Improved Signal Quality**: Focus on highest-probability setups
- **Enhanced Risk Management**: AI-optimized stop loss levels
- **Better Price Targets**: More realistic profit targets
- **Position Sizing**: Larger positions for highest confidence trades
- **Market Context**: Trading in sync with overall market conditions 