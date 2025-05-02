"""
AI Signal Ranking Module

This module provides AI/ML-based ranking of trade signals and GPT-powered market insights:
- Ranks trade signals based on historical performance
- Uses machine learning to score trade setups
- Leverages GPT models to analyze market trends and enhance trading decisions
"""

import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv
import json
import time

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AISignalRanking:
    """
    Provides AI-powered signal ranking and trading insights
    
    This class:
    - Ranks trade signals based on ML models
    - Provides GPT-powered market analysis
    - Enhances trade decisions with AI insights
    """
    
    def __init__(self, config, pnl_logger=None):
        """
        Initialize with configuration
        
        Args:
            config: Configuration dictionary or ExecutionModelConfig instance
            pnl_logger: Optional PnLLogger instance for historical data
        """
        self.config = config
        self.pnl_logger = pnl_logger
        
        # Get AI signal ranking configuration
        # Check if config is the ExecutionModelConfig object or a dictionary
        if hasattr(config, 'get'):
            # It's the ExecutionModelConfig object
            self.ai_config = config.get("ai_signal_ranking", {})
        else:
            # It's a dictionary
            self.ai_config = config.get("ai_signal_ranking", {}) if isinstance(config, dict) else {}
        
        # GPT API setup
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.openrouter_api_key:
            logger.warning("OpenRouter API key not found. GPT insights will not be available.")
        
        # Initialize OpenAI client if API key is available
        if self.openrouter_api_key:
            try:
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.openrouter_api_key,
                )
                logger.info("Successfully initialized OpenAI client")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {str(e)}")
                logger.error("GPT insights will be disabled")
                self.client = None
        else:
            self.client = None
        
        # Feature weights for signal ranking
        self.feature_weights = {
            'volume_ratio': self.ai_config.get('volume_weight', 0.25),
            'trend_strength': self.ai_config.get('trend_weight', 0.25),
            'historical_win_rate': self.ai_config.get('historical_weight', 0.3),
            'institutional_flow': self.ai_config.get('institutional_weight', 0.2),
        }
        
        # Load historical performance data if available
        self.historical_performance = self._load_historical_performance()
    
    def _load_historical_performance(self):
        """
        Load historical performance data for different symbols and setups
        
        Returns:
            DataFrame with historical performance metrics
        """
        try:
            if self.pnl_logger:
                # Get historical trade data from PnL logger
                trade_history = self.pnl_logger.get_trade_history()
                
                if not trade_history.empty:
                    # Calculate win rates by symbol and setup type
                    performance = {}
                    
                    # Group by symbol
                    by_symbol = trade_history.groupby('symbol')
                    for symbol, group in by_symbol:
                        wins = (group['pnl'] > 0).sum()
                        total = len(group)
                        win_rate = wins / total if total > 0 else 0.5
                        avg_pnl = group['pnl'].mean() if total > 0 else 0
                        
                        performance[symbol] = {
                            'win_rate': win_rate,
                            'avg_pnl': avg_pnl,
                            'trade_count': total
                        }
                    
                    # Group by setup type
                    by_setup = trade_history.groupby('strategy_name')
                    for setup, group in by_setup:
                        wins = (group['pnl'] > 0).sum()
                        total = len(group)
                        win_rate = wins / total if total > 0 else 0.5
                        avg_pnl = group['pnl'].mean() if total > 0 else 0
                        
                        performance[setup] = {
                            'win_rate': win_rate,
                            'avg_pnl': avg_pnl,
                            'trade_count': total
                        }
                        
                    return performance
            
            # Return default values if no data available
            return {}
            
        except Exception as e:
            logger.error(f"Error loading historical performance data: {str(e)}")
            return {}
    
    def rank_signals(self, signals, market_data):
        """
        Rank trade signals based on AI/ML models
        
        Args:
            signals: List of trade signal dictionaries
            market_data: Dictionary with market data for signals
            
        Returns:
            List of ranked signals with added confidence scores
        """
        if not signals:
            return []
            
        try:
            ranked_signals = []
            
            for signal in signals:
                symbol = signal.get('symbol')
                setup_type = signal.get('setup_type', 'UNKNOWN')
                
                # Skip if symbol not found in market data
                if symbol not in market_data:
                    logger.warning(f"No market data for {symbol}, skipping ranking")
                    signal['ai_confidence'] = 0.5  # Default confidence
                    signal['ranking_factors'] = {}
                    ranked_signals.append(signal)
                    continue
                
                # Calculate feature scores
                feature_scores = self._calculate_feature_scores(signal, market_data[symbol])
                
                # Calculate weighted confidence score
                confidence = 0
                for feature, score in feature_scores.items():
                    weight = self.feature_weights.get(feature, 0.1)
                    confidence += score * weight
                
                # Add AI confidence score and feature details to signal
                signal['ai_confidence'] = min(1.0, max(0.0, confidence))
                signal['ranking_factors'] = feature_scores
                ranked_signals.append(signal)
            
            # Sort signals by confidence score, highest first
            ranked_signals.sort(key=lambda x: x.get('ai_confidence', 0), reverse=True)
            
            return ranked_signals
            
        except Exception as e:
            logger.error(f"Error ranking signals: {str(e)}")
            return signals
    
    def _calculate_feature_scores(self, signal, market_data):
        """
        Calculate feature scores for a signal
        
        Args:
            signal: Trade signal dictionary
            market_data: Market data DataFrame for the signal's symbol
            
        Returns:
            Dictionary with feature scores (0-1 range)
        """
        symbol = signal.get('symbol')
        setup_type = signal.get('setup_type', 'UNKNOWN')
        direction = signal.get('direction', 'UNKNOWN')
        
        feature_scores = {}
        
        # 1. Volume ratio score
        try:
            recent_volume = market_data['volume'].iloc[-5:].mean()
            baseline_volume = market_data['volume'].iloc[-20:-5].mean()
            volume_ratio = recent_volume / baseline_volume if baseline_volume > 0 else 1
            
            # Score 0-1 based on volume ratio (higher volume is better)
            volume_score = min(1.0, volume_ratio / 3.0)
            feature_scores['volume_ratio'] = volume_score
        except:
            feature_scores['volume_ratio'] = 0.5
        
        # 2. Trend strength score
        try:
            # Calculate a simple trend metric
            close_prices = market_data['close'].iloc[-20:].values
            price_changes = np.diff(close_prices) / close_prices[:-1]
            
            # Direction of trend (-1 to 1)
            trend_direction = np.sum(np.sign(price_changes)) / len(price_changes)
            
            # Magnitude of trend (volatility-adjusted)
            trend_magnitude = abs(np.sum(price_changes)) / (np.std(price_changes) + 0.001)
            
            # Adjust score based on signal direction
            if direction == 'LONG':
                direction_factor = max(0, trend_direction)
            else:  # SHORT
                direction_factor = max(0, -trend_direction)
                
            # Combine direction and magnitude for trend score
            trend_score = min(1.0, (direction_factor * 0.5 + min(1.0, trend_magnitude / 5) * 0.5))
            feature_scores['trend_strength'] = trend_score
        except:
            feature_scores['trend_strength'] = 0.5
        
        # 3. Historical win rate score
        try:
            # Look up historical performance for this symbol and setup type
            symbol_perf = self.historical_performance.get(symbol, {})
            setup_perf = self.historical_performance.get(setup_type, {})
            
            # Calculate combined win rate, weighted by trade count
            symbol_win_rate = symbol_perf.get('win_rate', 0.5)
            symbol_count = symbol_perf.get('trade_count', 0)
            
            setup_win_rate = setup_perf.get('win_rate', 0.5)
            setup_count = setup_perf.get('trade_count', 0)
            
            # Weight by trade count to trust data with more samples
            if symbol_count + setup_count > 0:
                historical_win_rate = (symbol_win_rate * symbol_count + setup_win_rate * setup_count) / (symbol_count + setup_count)
            else:
                historical_win_rate = 0.5
                
            feature_scores['historical_win_rate'] = historical_win_rate
        except:
            feature_scores['historical_win_rate'] = 0.5
        
        # 4. Institutional flow score (placeholder)
        # In a complete implementation, this could use flow_indicator data
        feature_scores['institutional_flow'] = 0.5
        
        return feature_scores
    
    def get_gpt_insights(self, symbols, market_data, recent_signals=None, lookback_days=5):
        """
        Get GPT-powered market insights
        
        Args:
            symbols: List of symbols to analyze
            market_data: Dictionary of market data by symbol
            recent_signals: Optional list of recent trading signals
            lookback_days: Number of days to analyze
            
        Returns:
            Dictionary with GPT-powered market insights
        """
        try:
            # Check if GPT client is available
            if not self.client:
                logger.warning("GPT client not available, returning fallback insights")
                return self._generate_fallback_insights(symbols, market_data)
            
            # Prepare data for GPT
            prompt_data = {}
            for symbol in symbols[:3]:  # Limit to 3 symbols to avoid token limits
                if symbol in market_data:
                    try:
                        prompt_data[symbol] = self._prepare_data_for_gpt(symbol, market_data[symbol], lookback_days)
                    except Exception as symbol_error:
                        logger.error(f"Error preparing data for {symbol}: {str(symbol_error)}")
            
            if not prompt_data:
                logger.warning("No data could be prepared for GPT, returning fallback insights")
                return self._generate_fallback_insights(symbols, market_data)
            
            # Create GPT prompt
            prompt = self._create_market_analysis_prompt(prompt_data, recent_signals)
            
            # Call GPT API with retry logic
            try:
                max_retries = 2
                for attempt in range(max_retries + 1):
                    try:
                        response = self.client.chat.completions.create(
                            model="openai/gpt-4o",
                            messages=[
                                {"role": "system", "content": "You are an expert financial analyst and trader. Analyze market data and provide insights."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.2,
                            max_tokens=1000,
                        )
                        
                        # Process response
                        insights_text = response.choices[0].message.content
                        insights = self._parse_gpt_insights(insights_text)
                        
                        return insights
                        
                    except Exception as api_error:
                        if attempt < max_retries:
                            logger.warning(f"GPT API error, retrying ({attempt+1}/{max_retries}): {str(api_error)}")
                            time.sleep(2)  # Wait before retry
                        else:
                            raise api_error
                            
            except Exception as gpt_error:
                logger.error(f"Error calling GPT API: {str(gpt_error)}")
                return self._generate_fallback_insights(symbols, market_data)
            
        except Exception as e:
            logger.error(f"Error generating GPT insights: {str(e)}")
            return self._generate_fallback_insights(symbols, market_data)
        
    def _generate_fallback_insights(self, symbols, market_data):
        """
        Generate fallback insights when GPT is not available
        
        Args:
            symbols: List of symbols
            market_data: Market data dictionary
            
        Returns:
            Dictionary with basic market insights
        """
        insights = {
            'market_summary': "AI-powered market analysis is temporarily unavailable. Using algorithmic analysis instead.",
            'key_insights': [],
            'trade_opportunities': []
        }
        
        # Generate basic insights from market data
        for symbol in symbols:
            if symbol in market_data:
                try:
                    df = market_data[symbol]
                    
                    # Calculate basic metrics
                    last_price = df['close'].iloc[-1] if 'close' in df.columns and len(df) > 0 else None
                    prev_price = df['close'].iloc[-2] if 'close' in df.columns and len(df) > 1 else None
                    
                    if last_price and prev_price:
                        change_pct = (last_price - prev_price) / prev_price * 100
                        direction = 'bullish' if change_pct > 0 else 'bearish'
                        
                        insights['key_insights'].append({
                            'symbol': symbol,
                            'insight': f"{symbol} is showing {direction} momentum with {abs(change_pct):.2f}% change.",
                            'confidence': 60
                        })
                        
                        # Only add trade opportunities for significant moves
                        if abs(change_pct) > 1.5:
                            insights['trade_opportunities'].append({
                                'symbol': symbol,
                                'direction': 'BUY' if change_pct > 0 else 'SELL',
                                'reason': f"Significant {direction} price movement",
                                'conviction': 'medium'
                            })
                except Exception as symbol_error:
                    logger.error(f"Error generating fallback insights for {symbol}: {str(symbol_error)}")
        
        return insights
    
    def _prepare_data_for_gpt(self, symbol, market_data, lookback_days=5):
        """
        Prepare market data for GPT analysis
        
        Args:
            symbol: Symbol to analyze
            market_data: Market data DataFrame
            lookback_days: Days of data to include
            
        Returns:
            String with formatted market data summary
        """
        try:
            # Get recent data
            recent_data = market_data.tail(lookback_days * 8)  # Assuming 8 periods per day
            
            # Calculate some basic metrics
            current_price = recent_data['close'].iloc[-1]
            price_change = (current_price / recent_data['close'].iloc[0] - 1) * 100
            high = recent_data['high'].max()
            low = recent_data['low'].min()
            volume_change = (recent_data['volume'].iloc[-5:].mean() / recent_data['volume'].iloc[:-5].mean() - 1) * 100
            
            # Calculate daily ranges
            daily_highs = recent_data['high'].resample('D').max()
            daily_lows = recent_data['low'].resample('D').min()
            daily_range_avg = ((daily_highs - daily_lows) / daily_lows).mean() * 100
            
            # Format data summary
            data_summary = f"""
            Market data summary for {symbol}:
            
            Current price: ${current_price:.2f}
            {lookback_days}-day price change: {price_change:.2f}%
            {lookback_days}-day high: ${high:.2f}
            {lookback_days}-day low: ${low:.2f}
            Recent volume change: {volume_change:.2f}%
            Average daily range: {daily_range_avg:.2f}%
            
            Recent price data (last 10 periods):
            """
            
            # Add recent OHLCV data
            recent_rows = recent_data.tail(10).reset_index()
            for _, row in recent_rows.iterrows():
                data_summary += f"Time: {row['timestamp']} | Open: ${row['open']:.2f} | High: ${row['high']:.2f} | Low: ${row['low']:.2f} | Close: ${row['close']:.2f} | Volume: {row['volume']}\n"
            
            return data_summary
            
        except Exception as e:
            logger.error(f"Error preparing data for GPT: {str(e)}")
            return f"Error preparing data: {str(e)}"
    
    def optimize_trade_setup(self, trade_setup, market_data):
        """
        Optimize a trade setup using GPT insights
        
        Args:
            trade_setup: Trade setup dictionary
            market_data: Market data for the trade setup's symbol
            
        Returns:
            Optimized trade setup with AI-enhanced parameters
        """
        if not self.client:
            logger.warning("OpenAI client not initialized, cannot optimize trade setup.")
            return trade_setup
            
        try:
            symbol = trade_setup.get('symbol')
            if not symbol:
                logger.warning("No symbol in trade setup, cannot optimize")
                return trade_setup
            
            # Get GPT insights for this symbol
            try:
                insights = self.get_gpt_insights([symbol], {symbol: market_data})
                if not insights or symbol not in insights or "error" in insights.get(symbol, {}):
                    # If there was an error getting insights, just return the original setup
                    if insights and symbol in insights and "error" in insights[symbol]:
                        logger.warning(f"Error in GPT insights for {symbol}: {insights[symbol]['error']}")
                    return trade_setup
                
                symbol_insights = insights[symbol]
                
                # Create an optimized copy of the trade setup
                optimized_setup = trade_setup.copy()
                
                # Add insights to the setup
                optimized_setup['ai_insights'] = symbol_insights
                
                # Optimize stop loss if suggested in insights
                if 'stop_loss' in symbol_insights:
                    suggested_stop = symbol_insights['stop_loss']
                    if isinstance(suggested_stop, (int, float)) and suggested_stop > 0:
                        # Only adjust if the suggested stop is logical
                        current_stop = trade_setup.get('stop_loss', 0)
                        entry_price = trade_setup.get('entry_price', 0)
                        direction = trade_setup.get('direction', 'LONG')
                        
                        if direction == 'LONG' and suggested_stop < entry_price:
                            # For long trades, stop loss should be below entry
                            optimized_setup['stop_loss'] = suggested_stop
                            optimized_setup['stop_loss_reason'] = 'AI-suggested support level'
                        elif direction == 'SHORT' and suggested_stop > entry_price:
                            # For short trades, stop loss should be above entry
                            optimized_setup['stop_loss'] = suggested_stop
                            optimized_setup['stop_loss_reason'] = 'AI-suggested resistance level'
                        
                # Optimize profit target if suggested in insights
                if 'take_profit' in symbol_insights:
                    suggested_target = symbol_insights['take_profit']
                    if isinstance(suggested_target, (int, float)) and suggested_target > 0:
                        # Only adjust if the suggested target is logical
                        current_target = trade_setup.get('profit_target', 0)
                        entry_price = trade_setup.get('entry_price', 0)
                        direction = trade_setup.get('direction', 'LONG')
                        
                        if direction == 'LONG' and suggested_target > entry_price:
                            # For long trades, target should be above entry
                            optimized_setup['profit_target'] = suggested_target
                            optimized_setup['profit_target_reason'] = 'AI-suggested resistance level'
                        elif direction == 'SHORT' and suggested_target < entry_price:
                            # For short trades, target should be below entry
                            optimized_setup['profit_target'] = suggested_target
                            optimized_setup['profit_target_reason'] = 'AI-suggested support level'
                
                # Add setup quality from insights
                if 'setup_quality' in symbol_insights:
                    setup_quality = symbol_insights['setup_quality']
                    if isinstance(setup_quality, (int, float)):
                        # Convert to 0-1 scale
                        optimized_setup['ai_setup_quality'] = min(max(setup_quality / 10.0, 0), 1)
                
                # Add tradable bias from insights
                if 'bias' in symbol_insights:
                    bias = symbol_insights['bias']
                    optimized_setup['ai_bias'] = bias
                
                return optimized_setup
            except Exception as insights_error:
                logger.error(f"Error getting insights for trade optimization: {str(insights_error)}")
                return trade_setup
            
        except Exception as e:
            logger.error(f"Error optimizing trade setup: {str(e)}")
            return trade_setup
    
    def get_market_summary(self, market_data, top_symbols=None):
        """
        Get a GPT-powered summary of overall market conditions
        
        Args:
            market_data: Dictionary with market data for multiple symbols
            top_symbols: Optional list of symbols to focus on
            
        Returns:
            Dictionary with market summary insights
        """
        if not self.client:
            logger.warning("OpenAI client not initialized, cannot get market summary.")
            return {
                "market_sentiment": "Neutral",
                "trend": "Sideways",
                "risks": "Unable to analyze - no API access",
                "opportunities": "Unable to analyze - no API access",
                "volatility": "Unknown",
                "trading_approach": "Cautious"
            }
            
        try:
            # Select symbols to include in summary
            if top_symbols:
                symbols = top_symbols
            else:
                symbols = list(market_data.keys())[:5]  # Limit to 5 symbols
            
            # Prepare market summary
            market_summary = "Market data summary for overall analysis:\n\n"
            
            for symbol in symbols:
                if symbol not in market_data:
                    continue
                    
                data = market_data[symbol]
                if len(data) < 20:
                    continue
                    
                recent_data = data.tail(20)
                current_price = recent_data['close'].iloc[-1]
                price_change = (current_price / recent_data['close'].iloc[0] - 1) * 100
                
                market_summary += f"{symbol}: ${current_price:.2f} ({price_change:+.2f}%)\n"
            
            # Create prompt for overall market analysis
            prompt = f"""
            You are a professional market analysis assistant helping improve trading decisions.
            
            Analyze the following market overview and provide a concise summary of current market conditions:
            
            {market_summary}
            
            Provide a concise analysis with:
            1. Overall market sentiment and trend
            2. Key market risks and opportunities
            3. Sector or asset class rotation insights
            4. Volatility assessment
            5. Suggested trading approach for current conditions
            
            Format your response as structured JSON with keys: market_sentiment, trend, risks, opportunities, volatility, trading_approach, additional_notes.
            """
            
            try:
                # Call GPT API
                response = self.client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": "ai-trading-bot.app", 
                        "X-Title": "AI Trading Bot",
                    },
                    model="anthropic/claude-3.7-sonnet",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                if response and hasattr(response, 'choices') and len(response.choices) > 0:
                    insight_text = response.choices[0].message.content
                    
                    # Parse JSON response
                    try:
                        # Extract JSON content if it's wrapped in markdown code blocks
                        if '```json' in insight_text and '```' in insight_text:
                            json_text = insight_text.split('```json')[1].split('```')[0].strip()
                        elif '```' in insight_text:
                            json_text = insight_text.split('```')[1].split('```')[0].strip()
                        else:
                            json_text = insight_text
                            
                        return json.loads(json_text)
                    except Exception as e:
                        logger.error(f"Error parsing GPT response for market summary: {str(e)}")
                        return {
                            "error": "Failed to parse response", 
                            "raw_text": insight_text,
                            "market_sentiment": "Error analyzing",
                            "trend": "Unknown",
                            "risks": "Unable to analyze - parsing error",
                            "opportunities": "Unable to analyze - parsing error",
                            "volatility": "Unknown",
                            "trading_approach": "Cautious"
                        }
                else:
                    return {
                        "error": "No valid response from API",
                        "market_sentiment": "Error analyzing",
                        "trend": "Unknown",
                        "risks": "Unable to analyze - API error",
                        "opportunities": "Unable to analyze - API error",
                        "volatility": "Unknown",
                        "trading_approach": "Cautious"
                    }
            except Exception as api_error:
                logger.error(f"API error for market summary: {str(api_error)}")
                return {
                    "error": f"API error: {str(api_error)}",
                    "market_sentiment": "Error analyzing",
                    "trend": "Unknown",
                    "risks": "Unable to analyze - API error",
                    "opportunities": "Unable to analyze - API error",
                    "volatility": "Unknown",
                    "trading_approach": "Cautious"
                }
                
        except Exception as e:
            logger.error(f"Error getting market summary: {str(e)}")
            return {
                "error": str(e),
                "market_sentiment": "Error analyzing",
                "trend": "Unknown",
                "risks": "Unable to analyze - error",
                "opportunities": "Unable to analyze - error",
                "volatility": "Unknown",
                "trading_approach": "Cautious"
            }
    
    def _create_market_analysis_prompt(self, prompt_data, recent_signals=None):
        """
        Create a prompt for market analysis
        
        Args:
            prompt_data: Dictionary with prepared data for each symbol
            recent_signals: Optional list of recent signals
            
        Returns:
            String prompt for the GPT model
        """
        prompt = """
        You are a professional market analyst providing insights to a trader.
        Analyze the following market data and provide strategic trading insights.
        
        """
        
        # Add market data for each symbol
        for symbol, data in prompt_data.items():
            prompt += f"\n## {symbol} Market Data:\n{data}\n"
        
        # Add recent signals if available
        if recent_signals:
            prompt += "\n## Recent Trading Signals:\n"
            for signal in recent_signals[:5]:  # Limit to 5 recent signals
                symbol = signal.get('symbol', 'UNKNOWN')
                direction = signal.get('direction', 'UNKNOWN')
                setup_type = signal.get('setup_type', 'UNKNOWN')
                confidence = signal.get('ai_confidence', 0)
                
                prompt += f"- {symbol}: {direction} signal from {setup_type} setup (confidence: {confidence:.2f})\n"
        
        # Specify the desired format for the response
        prompt += """
        Please provide a comprehensive market analysis including:
        
        1. Market Summary: Overall assessment of the current market conditions
        2. Key Market Trends: Identify 2-3 significant market trends
        3. Trading Opportunities: List 2-3 specific trading opportunities with:
           - Symbol
           - Direction (BUY/SELL)
           - Entry strategy
           - Stop loss recommendation
           - Target price
           - Rationale
        
        Keep your analysis evidence-based, focusing on price action, volume, and technical indicators.
        """
        
        return prompt
    
    def _parse_gpt_insights(self, insights_text):
        """
        Parse GPT response into structured insights
        
        Args:
            insights_text: Raw text response from GPT
            
        Returns:
            Dictionary with structured insights
        """
        try:
            # Check if response contains JSON
            if '```json' in insights_text:
                json_start = insights_text.find('```json') + 7
                json_end = insights_text.find('```', json_start)
                if json_end > json_start:
                    json_content = insights_text[json_start:json_end].strip()
                    try:
                        return json.loads(json_content)
                    except json.JSONDecodeError:
                        pass  # Fall back to text parsing
            
            # Parse as text when JSON parsing fails
            insights = {
                'market_summary': "",
                'key_trends': [],
                'trade_opportunities': []
            }
            
            # Parse market summary
            if "Market Summary:" in insights_text:
                summary_start = insights_text.find("Market Summary:") + 15
                summary_end = insights_text.find("\n\n", summary_start)
                if summary_end == -1:
                    summary_end = len(insights_text)
                insights['market_summary'] = insights_text[summary_start:summary_end].strip()
            
            # Parse key trends
            if "Key Market Trends:" in insights_text:
                trends_start = insights_text.find("Key Market Trends:") + 18
                trends_end = insights_text.find("\n\n", trends_start)
                if trends_end == -1:
                    trends_end = len(insights_text)
                trends_text = insights_text[trends_start:trends_end].strip()
                
                # Extract individual trends
                trend_lines = [line.strip() for line in trends_text.split('\n') if line.strip() and not line.strip().startswith("Key Market Trends:")]
                
                for line in trend_lines:
                    if line.startswith("-") or line.startswith("*"):
                        insights['key_trends'].append(line[1:].strip())
                    elif line[0].isdigit() and line[1] in [".", ")"]:
                        insights['key_trends'].append(line[2:].strip())
                    else:
                        insights['key_trends'].append(line)
            
            # Parse trading opportunities
            if "Trading Opportunities:" in insights_text:
                opps_start = insights_text.find("Trading Opportunities:") + 22
                opps_section = insights_text[opps_start:].strip()
                
                # Look for symbol patterns
                import re
                symbol_matches = re.findall(r'([A-Z]{1,5}):\s*(BUY|SELL|Long|Short)', opps_section)
                
                for symbol, direction in symbol_matches:
                    # Normalize direction
                    direction = direction.upper()
                    if direction == "LONG":
                        direction = "BUY"
                    elif direction == "SHORT":
                        direction = "SELL"
                    
                    # Find relevant section for this symbol
                    symbol_start = opps_section.find(f"{symbol}:")
                    next_symbol_match = re.search(r'([A-Z]{1,5}):\s*(BUY|SELL|Long|Short)', opps_section[symbol_start+len(symbol)+1:])
                    if next_symbol_match:
                        next_symbol_start = opps_section.find(next_symbol_match.group(0), symbol_start+len(symbol)+1)
                        symbol_section = opps_section[symbol_start:next_symbol_start]
                    else:
                        symbol_section = opps_section[symbol_start:]
                    
                    # Extract rationale
                    rationale = ""
                    if "Rationale:" in symbol_section:
                        rationale_start = symbol_section.find("Rationale:") + 10
                        rationale_end = symbol_section.find("\n\n", rationale_start)
                        if rationale_end == -1:
                            rationale_end = len(symbol_section)
                        rationale = symbol_section[rationale_start:rationale_end].strip()
                    
                    # Extract stop loss
                    stop_loss = None
                    stop_loss_match = re.search(r'Stop Loss:?\s*([\d\.]+)', symbol_section)
                    if stop_loss_match:
                        try:
                            stop_loss = float(stop_loss_match.group(1))
                        except:
                            pass
                    
                    # Extract target
                    target = None
                    target_match = re.search(r'Target:?\s*([\d\.]+)', symbol_section)
                    if target_match:
                        try:
                            target = float(target_match.group(1))
                        except:
                            pass
                    
                    # Add opportunity
                    insights['trade_opportunities'].append({
                        'symbol': symbol,
                        'direction': direction,
                        'rationale': rationale,
                        'stop_loss': stop_loss,
                        'target': target
                    })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error parsing GPT insights: {str(e)}")
            return {
                'market_summary': "Error parsing AI insights, please try again later.",
                'key_trends': [],
                'trade_opportunities': []
            } 