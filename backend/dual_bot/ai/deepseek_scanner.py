"""
DeepSeek scanner module for analyzing market data and generating trade recommendations.
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import time

from ..config.config_loader import load_config
from ..data.data_fetcher import DataFetcher

# Initialize logger
logger = logging.getLogger(__name__)

class DeepSeekScanner:
    """Scanner for identifying high-probability 0DTE options trades."""
    
    def __init__(self, config: Dict):
        """
        Initialize DeepSeek scanner.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.symbols = self.config["trading"]["symbols"]
        self.max_trades_per_day = self.config["trading"]["max_trades_per_day"]
        
        # Get thresholds from config with defaults if not present
        self.thresholds = self.config["trading"].get("signal_thresholds", {})
        self.flow_score_threshold = self.thresholds.get("flow_score_threshold", 0.7)
        self.dark_pool_score_threshold = self.thresholds.get("dark_pool_score_threshold", 0.7)
        self.news_score_threshold = self.thresholds.get("news_score_threshold", 0.8)
        self.technical_score_threshold = self.thresholds.get("technical_score_threshold", 0.6)
        self.combined_score_threshold = self.thresholds.get("combined_score_threshold", 0.65)
        
        self.trades_today = 0
        self.last_recommendations = []
        self.data_cache = {
            "market_data": {},
            "options_flow": [],
            "dark_pool": [],
            "news": []
        }
        self.is_running = False
        
        # Initialize data fetcher
        self.data_fetcher = DataFetcher()
        self.data_fetcher.initialize()
        
        # Set up callbacks
        self.data_fetcher.set_market_data_callback(self._on_market_data)
        self.data_fetcher.set_options_flow_callback(self._on_options_flow)
        self.data_fetcher.set_dark_pool_callback(self._on_dark_pool)
        self.data_fetcher.set_news_callback(self._on_news)
        
        logger.info(f"DeepSeekScanner initialized with thresholds: flow={self.flow_score_threshold}, dark_pool={self.dark_pool_score_threshold}, news={self.news_score_threshold}")
    
    def start(self):
        """Start the scanner."""
        if not self.is_running:
            logger.info("Starting DeepSeek Scanner...")
            self.is_running = True
            self.data_fetcher.start()
            logger.info("DeepSeek Scanner started successfully!")
            return True
        return False
    
    def stop(self):
        """Stop the scanner."""
        if self.is_running:
            logger.info("Stopping DeepSeek Scanner...")
            self.is_running = False
            self.data_fetcher.stop()
            logger.info("DeepSeek Scanner stopped successfully!")
            return True
        return False
    
    def _on_market_data(self, symbol: str, data: Dict):
        """Handle incoming market data."""
        try:
            # Process market data and update internal state
            if symbol in self.symbols:
                self._analyze_market_data(symbol, data)
                # Cache market data
                self.data_cache["market_data"][symbol] = data
        except Exception as e:
            logger.error(f"Error processing market data: {e}")
    
    def _on_options_flow(self, data: List[Dict]):
        """Handle options flow data."""
        try:
            # Process options flow data
            self._analyze_options_flow(data)
            # Cache options flow data
            self.data_cache["options_flow"] = data
        except Exception as e:
            logger.error(f"Error processing options flow: {e}")
    
    def _on_dark_pool(self, data: List[Dict]):
        """Handle dark pool data."""
        try:
            # Process dark pool data
            self._analyze_dark_pool(data)
            # Cache dark pool data
            self.data_cache["dark_pool"] = data
        except Exception as e:
            logger.error(f"Error processing dark pool data: {e}")
    
    def _on_news(self, data: List[Dict]):
        """Handle news data."""
        try:
            # Process news data
            self._analyze_news(data)
            # Cache news data
            self.data_cache["news"] = data
        except Exception as e:
            logger.error(f"Error processing news data: {e}")
    
    def _analyze_market_data(self, symbol: str, data: Dict):
        """
        Analyze market data for trading opportunities.
        
        Args:
            symbol: Stock symbol
            data: Market data
        """
        # Get historical data for technical analysis
        market_data = self.data_fetcher.get_market_data(symbol)
        if not market_data:
            return
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(market_data)
        
        # Calculate technical indicators
        df = self._calculate_indicators(df)
        
        # Check for trading signals
        signals = self._generate_signals(df)
        
        # Update recommendations if strong signals found
        if signals:
            self._update_recommendations(symbol, signals)
    
    def _analyze_options_flow(self, data: List[Dict]):
        """
        Analyze options flow data for unusual activity.
        
        Args:
            data: List of options flow trades
        """
        for flow in data:
            # Calculate flow score
            score = self._calculate_flow_score(flow)
            
            # If score exceeds threshold, update recommendations
            if score >= self.flow_score_threshold:
                self._update_recommendations(flow["symbol"], [{
                    "type": "options_flow",
                    "score": score,
                    "data": flow
                }])
    
    def _analyze_dark_pool(self, data: List[Dict]):
        """
        Analyze dark pool data for institutional activity.
        
        Args:
            data: List of dark pool trades
        """
        for trade in data:
            # Calculate dark pool score
            score = self._calculate_dark_pool_score(trade)
            
            # If score exceeds threshold, update recommendations
            if score >= self.dark_pool_score_threshold:
                self._update_recommendations(trade["symbol"], [{
                    "type": "dark_pool",
                    "score": score,
                    "data": trade
                }])
    
    def _analyze_news(self, data: List[Dict]):
        """
        Analyze news data for market impact.
        
        Args:
            data: List of news articles
        """
        for article in data:
            # Calculate news score
            score = self._calculate_news_score(article)
            
            # If score exceeds threshold, update recommendations
            if score >= self.news_score_threshold:
                self._update_recommendations(article["symbol"], [{
                    "type": "news",
                    "score": score,
                    "data": article
                }])
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for analysis.
        
        Args:
            df: DataFrame with market data
            
        Returns:
            DataFrame with added indicators
        """
        # Calculate RSI
        df["rsi"] = self._calculate_rsi(df["close"])
        
        # Calculate MACD
        df["macd"], df["macd_signal"] = self._calculate_macd(df["close"])
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(
        self,
        prices: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD and signal line."""
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd, signal_line
    
    def _generate_signals(self, df: pd.DataFrame) -> List[Dict]:
        """
        Generate trading signals based on technical indicators.
        
        Args:
            df: DataFrame with technical indicators
            
        Returns:
            List of trading signals
        """
        signals = []
        
        # Get latest values
        latest = df.iloc[-1]
        
        # Check RSI
        if latest["rsi"] < 30:
            strength = 1 - (latest["rsi"] / 30)
            if strength >= self.technical_score_threshold:
                signals.append({
                    "type": "indicator",
                    "direction": "bullish",
                    "strength": strength,
                    "indicator": "rsi",
                    "value": latest["rsi"]
                })
        elif latest["rsi"] > 70:
            strength = (latest["rsi"] - 70) / 30
            if strength >= self.technical_score_threshold:
                signals.append({
                    "type": "indicator",
                    "direction": "bearish",
                    "strength": strength,
                    "indicator": "rsi",
                    "value": latest["rsi"]
                })
        
        # Check MACD
        if latest["macd"] > latest["macd_signal"]:
            strength = (latest["macd"] - latest["macd_signal"]) / latest["macd"] if latest["macd"] != 0 else 0
            if strength >= self.technical_score_threshold:
                signals.append({
                    "type": "indicator",
                    "direction": "bullish",
                    "strength": strength,
                    "indicator": "macd",
                    "value": latest["macd"]
                })
        elif latest["macd"] < latest["macd_signal"]:
            strength = (latest["macd_signal"] - latest["macd"]) / latest["macd_signal"] if latest["macd_signal"] != 0 else 0
            if strength >= self.technical_score_threshold:
                signals.append({
                    "type": "indicator",
                    "direction": "bearish",
                    "strength": strength,
                    "indicator": "macd",
                    "value": latest["macd"]
                })
        
        return signals
    
    def _calculate_flow_score(self, flow: Dict) -> float:
        """
        Calculate score for options flow trade.
        
        Args:
            flow: Options flow trade data
            
        Returns:
            Score between 0 and 1
        """
        score = 0.0
        
        # Volume factor
        volume = flow.get("volume", 0)
        if volume > 1000:
            score += 0.3
        elif volume > 500:
            score += 0.2
        elif volume > 100:
            score += 0.1
        
        # Premium factor
        premium = flow.get("premium", 0)
        if premium > 100000:
            score += 0.3
        elif premium > 50000:
            score += 0.2
        elif premium > 10000:
            score += 0.1
        
        # Time factor (closer to market open = higher score)
        time = flow.get("time", "")
        if time:
            try:
                trade_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
                market_open = trade_time.replace(hour=9, minute=30, second=0)
                minutes_from_open = (trade_time - market_open).total_seconds() / 60
                if minutes_from_open <= 30:
                    score += 0.4
                elif minutes_from_open <= 60:
                    score += 0.2
            except:
                pass
        
        return min(score, 1.0)
    
    def _calculate_dark_pool_score(self, trade: Dict) -> float:
        """
        Calculate score for dark pool trade.
        
        Args:
            trade: Dark pool trade data
            
        Returns:
            Score between 0 and 1
        """
        score = 0.0
        
        # Size factor
        size = trade.get("size", 0)
        if size > 10000:
            score += 0.4
        elif size > 5000:
            score += 0.3
        elif size > 1000:
            score += 0.2
        
        # Price impact factor
        price_impact = trade.get("price_impact", 0)
        if price_impact > 0.02:
            score += 0.3
        elif price_impact > 0.01:
            score += 0.2
        elif price_impact > 0.005:
            score += 0.1
        
        # Time factor
        time = trade.get("time", "")
        if time:
            try:
                trade_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
                market_open = trade_time.replace(hour=9, minute=30, second=0)
                minutes_from_open = (trade_time - market_open).total_seconds() / 60
                if minutes_from_open <= 30:
                    score += 0.3
                elif minutes_from_open <= 60:
                    score += 0.2
            except:
                pass
        
        return min(score, 1.0)
    
    def _calculate_news_score(self, article: Dict) -> float:
        """
        Calculate score for news article.
        
        Args:
            article: News article data
            
        Returns:
            Score between 0 and 1
        """
        score = 0.0
        
        # Source factor
        source = article.get("source", "").lower()
        if "reuters" in source or "bloomberg" in source:
            score += 0.4
        elif "yahoo" in source or "cnbc" in source:
            score += 0.3
        elif "marketwatch" in source:
            score += 0.2
        
        # Time factor
        published_at = article.get("publishedAt", "")
        if published_at:
            try:
                article_time = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                market_open = article_time.replace(hour=9, minute=30, second=0)
                minutes_from_open = (article_time - market_open).total_seconds() / 60
                if minutes_from_open <= 30:
                    score += 0.3
                elif minutes_from_open <= 60:
                    score += 0.2
            except:
                pass
        
        # Sentiment factor (if available)
        sentiment = article.get("sentiment", 0)
        if sentiment > 0.7:
            score += 0.3
        elif sentiment > 0.5:
            score += 0.2
        elif sentiment > 0.3:
            score += 0.1
        
        return min(score, 1.0)
    
    def _update_recommendations(self, symbol: str, signals: List[Dict]):
        """
        Update trade recommendations based on signals.
        
        Args:
            symbol: Stock symbol
            signals: List of trading signals
        """
        # Check if we've reached daily trade limit
        if self.trades_today >= self.max_trades_per_day:
            return
        
        # Calculate overall score
        total_score = sum(signal.get("strength", 0) for signal in signals)
        avg_score = total_score / len(signals)
        
        # Check if score exceeds combined threshold
        if avg_score < self.combined_score_threshold:
            logger.info(f"Signal for {symbol} with score {avg_score:.2f} below threshold {self.combined_score_threshold}")
            return
        
        # Create recommendation
        recommendation = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "score": avg_score,
            "signals": signals,
            "direction": "bullish" if avg_score > 0.5 else "bearish",
            # Add additional fields needed by run_bot.py
            "entry_price": self._get_current_price(symbol),
            "stop_loss": self._calculate_stop_loss(symbol, "bullish" if avg_score > 0.5 else "bearish"),
            "take_profit": self._calculate_take_profit(symbol, "bullish" if avg_score > 0.5 else "bearish")
        }
        
        # Add to recommendations
        self.last_recommendations.append(recommendation)
        
        # Sort by score and keep only top 3
        self.last_recommendations.sort(key=lambda x: x["score"], reverse=True)
        self.last_recommendations = self.last_recommendations[:3]
        
        # Increment trade count
        self.trades_today += 1
        
        logger.info(f"Added new recommendation for {symbol} with score {avg_score:.2f}")
    
    def _get_current_price(self, symbol: str) -> float:
        """Get current price for symbol."""
        try:
            # Try to get price from data cache
            if symbol in self.data_cache["market_data"]:
                return self.data_cache["market_data"][symbol].get("close", 0.0)
            
            # If not in cache, try to get from data fetcher
            market_data = self.data_fetcher.get_market_data(symbol)
            if market_data and len(market_data) > 0:
                return market_data[-1].get("close", 0.0)
            
            # Default value if no data available
            return 0.0
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return 0.0
    
    def _calculate_stop_loss(self, symbol: str, direction: str) -> float:
        """Calculate stop loss price based on risk parameters."""
        try:
            current_price = self._get_current_price(symbol)
            stop_loss_percent = self.config["trading"]["risk_management"]["default_stop_loss_percent"] / 100.0
            
            if direction == "bullish":
                return round(current_price * (1 - stop_loss_percent), 2)
            else:
                return round(current_price * (1 + stop_loss_percent), 2)
        except Exception as e:
            logger.error(f"Error calculating stop loss for {symbol}: {e}")
            return 0.0
    
    def _calculate_take_profit(self, symbol: str, direction: str) -> float:
        """Calculate take profit price based on risk parameters."""
        try:
            current_price = self._get_current_price(symbol)
            take_profit_percent = self.config["trading"]["risk_management"]["default_take_profit_percent"] / 100.0
            
            if direction == "bullish":
                return round(current_price * (1 + take_profit_percent), 2)
            else:
                return round(current_price * (1 - take_profit_percent), 2)
        except Exception as e:
            logger.error(f"Error calculating take profit for {symbol}: {e}")
            return 0.0
    
    def get_recommendations(self, limit: int = 3) -> List[Dict]:
        """
        Get current trade recommendations.
        
        Args:
            limit: Maximum number of recommendations to return
            
        Returns:
            List of trade recommendations
        """
        return self.last_recommendations[:limit]
    
    def reset_daily_counts(self):
        """Reset daily trade counts."""
        self.trades_today = 0
    
    def generate_recommendations(self, force_update: bool = False) -> List[Dict]:
        """
        Generate trade recommendations.
        
        Args:
            force_update: Force update of recommendations regardless of daily limit
            
        Returns:
            List of trade recommendations
        """
        logger.info("Generating trade recommendations...")
        
        try:
            # If force_update, reset daily trade count
            if force_update:
                self.reset_daily_counts()
            
            # Check if we've reached daily trade limit
            if self.trades_today >= self.max_trades_per_day and not force_update:
                logger.info(f"Daily trade limit reached ({self.max_trades_per_day}). Returning current recommendations.")
                return self.get_recommendations()
            
            # Force refresh data for all symbols
            for symbol in self.symbols:
                try:
                    # Trigger data fetch with retries
                    self._fetch_with_retries(symbol)
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {e}")
            
            # Return current recommendations
            return self.get_recommendations()
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _fetch_with_retries(self, symbol: str, max_retries: int = 3, retry_delay: int = 2):
        """Fetch data with retries."""
        for attempt in range(max_retries):
            try:
                # Attempt to fetch market data
                market_data = self.data_fetcher.get_market_data(symbol)
                
                if market_data:
                    # Process the data
                    df = pd.DataFrame(market_data)
                    df = self._calculate_indicators(df)
                    signals = self._generate_signals(df)
                    
                    if signals:
                        self._update_recommendations(symbol, signals)
                    
                    return True
                
                # If no data, retry
                if attempt < max_retries - 1:
                    logger.warning(f"No data for {symbol}, retrying in {retry_delay} seconds (attempt {attempt+1}/{max_retries})...")
                    time.sleep(retry_delay)
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Error fetching data for {symbol}, retrying in {retry_delay} seconds (attempt {attempt+1}/{max_retries}): {e}")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Failed to fetch data for {symbol} after {max_retries} attempts: {e}")
                    raise
        
        return False 