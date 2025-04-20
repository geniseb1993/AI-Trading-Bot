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

from dual_bot.config import config, logger
from dual_bot.data_fetcher import DataFetcher

class DeepSeekScanner:
    """Scanner for identifying high-probability 0DTE options trades."""
    
    def __init__(self, data_fetcher: DataFetcher):
        """
        Initialize DeepSeek scanner.
        
        Args:
            data_fetcher: DataFetcher instance for market data
        """
        self.config = config
        self.data_fetcher = data_fetcher
        self.symbols = self.config["trading"]["symbols"]
        self.max_trades_per_day = self.config["trading"]["max_trades_per_day"]
        self.trades_today = 0
        self.last_recommendations = []
        
        # Set up callbacks
        self.data_fetcher.set_market_data_callback(self._on_market_data)
        self.data_fetcher.set_options_flow_callback(self._on_options_flow)
        self.data_fetcher.set_dark_pool_callback(self._on_dark_pool)
        self.data_fetcher.set_news_callback(self._on_news)
    
    def _on_market_data(self, symbol: str, data: Dict):
        """Handle incoming market data."""
        try:
            # Process market data and update internal state
            if symbol in self.symbols:
                self._analyze_market_data(symbol, data)
        except Exception as e:
            logger.error(f"Error processing market data: {e}")
    
    def _on_options_flow(self, data: List[Dict]):
        """Handle options flow data."""
        try:
            # Process options flow data
            self._analyze_options_flow(data)
        except Exception as e:
            logger.error(f"Error processing options flow: {e}")
    
    def _on_dark_pool(self, data: List[Dict]):
        """Handle dark pool data."""
        try:
            # Process dark pool data
            self._analyze_dark_pool(data)
        except Exception as e:
            logger.error(f"Error processing dark pool data: {e}")
    
    def _on_news(self, data: List[Dict]):
        """Handle news data."""
        try:
            # Process news data
            self._analyze_news(data)
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
            data: Options flow data
        """
        if not data:
            return
        
        # Filter for relevant symbols
        relevant_flow = [
            flow for flow in data
            if flow.get("symbol") in self.symbols
        ]
        
        # Analyze for unusual patterns
        for flow in relevant_flow:
            score = self._calculate_flow_score(flow)
            if score > 0.8:  # High confidence threshold
                self._update_recommendations(
                    symbol=flow["symbol"],
                    signals=[{
                        "type": "options_flow",
                        "direction": flow.get("direction"),
                        "confidence": score,
                        "details": flow
                    }]
                )
    
    def _analyze_dark_pool(self, data: List[Dict]):
        """
        Analyze dark pool data for institutional activity.
        
        Args:
            data: Dark pool data
        """
        if not data:
            return
        
        # Filter for relevant symbols
        relevant_trades = [
            trade for trade in data
            if trade.get("symbol") in self.symbols
        ]
        
        # Analyze for significant institutional activity
        for trade in relevant_trades:
            score = self._calculate_dark_pool_score(trade)
            if score > 0.7:  # Significant activity threshold
                self._update_recommendations(
                    symbol=trade["symbol"],
                    signals=[{
                        "type": "dark_pool",
                        "direction": "bullish" if trade.get("side") == "buy" else "bearish",
                        "confidence": score,
                        "details": trade
                    }]
                )
    
    def _analyze_news(self, data: List[Dict]):
        """
        Analyze news data for market-moving events.
        
        Args:
            data: News data
        """
        if not data:
            return
        
        # Filter for relevant symbols
        for symbol in self.symbols:
            relevant_news = [
                article for article in data
                if symbol.lower() in article.get("title", "").lower()
                or symbol.lower() in article.get("description", "").lower()
            ]
            
            # Analyze sentiment and impact
            for article in relevant_news:
                score = self._calculate_news_score(article)
                if abs(score) > 0.6:  # Significant news threshold
                    self._update_recommendations(
                        symbol=symbol,
                        signals=[{
                            "type": "news",
                            "direction": "bullish" if score > 0 else "bearish",
                            "confidence": abs(score),
                            "details": article
                        }]
                    )
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for analysis.
        
        Args:
            df: DataFrame with market data
            
        Returns:
            DataFrame with added indicators
        """
        # Add basic indicators
        df["ema_9"] = df["price"].ewm(span=9, adjust=False).mean()
        df["ema_21"] = df["price"].ewm(span=21, adjust=False).mean()
        df["volume_sma"] = df["volume"].rolling(window=20).mean()
        
        # Add momentum indicators
        df["rsi"] = self._calculate_rsi(df["price"])
        df["macd"], df["macd_signal"] = self._calculate_macd(df["price"])
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator."""
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
        """Calculate MACD indicator."""
        fast_ema = prices.ewm(span=fast, adjust=False).mean()
        slow_ema = prices.ewm(span=slow, adjust=False).mean()
        macd = fast_ema - slow_ema
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        return macd, macd_signal
    
    def _generate_signals(self, df: pd.DataFrame) -> List[Dict]:
        """
        Generate trading signals from technical analysis.
        
        Args:
            df: DataFrame with indicators
            
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        # Check for trend signals
        if df["ema_9"].iloc[-1] > df["ema_21"].iloc[-1] and df["ema_9"].iloc[-2] <= df["ema_21"].iloc[-2]:
            signals.append({
                "type": "trend",
                "direction": "bullish",
                "confidence": 0.7,
                "details": {
                    "indicator": "ema_crossover",
                    "value": df["ema_9"].iloc[-1]
                }
            })
        
        # Check for momentum signals
        rsi = df["rsi"].iloc[-1]
        if rsi < 30:
            signals.append({
                "type": "momentum",
                "direction": "bullish",
                "confidence": 0.6,
                "details": {
                    "indicator": "rsi_oversold",
                    "value": rsi
                }
            })
        elif rsi > 70:
            signals.append({
                "type": "momentum",
                "direction": "bearish",
                "confidence": 0.6,
                "details": {
                    "indicator": "rsi_overbought",
                    "value": rsi
                }
            })
        
        # Check for volume signals
        current_volume = df["volume"].iloc[-1]
        avg_volume = df["volume_sma"].iloc[-1]
        if current_volume > 2 * avg_volume:
            signals.append({
                "type": "volume",
                "direction": "neutral",
                "confidence": 0.5,
                "details": {
                    "indicator": "volume_surge",
                    "value": current_volume / avg_volume
                }
            })
        
        return signals
    
    def _calculate_flow_score(self, flow: Dict) -> float:
        """
        Calculate confidence score for options flow signal.
        
        Args:
            flow: Options flow data
            
        Returns:
            Confidence score between 0 and 1
        """
        score = 0.0
        
        # Premium threshold
        premium = flow.get("premium", 0)
        if premium > 1000000:  # Large order
            score += 0.3
        elif premium > 500000:  # Medium order
            score += 0.2
        elif premium > 100000:  # Small order
            score += 0.1
        
        # Unusual volume
        if flow.get("unusual_volume", False):
            score += 0.2
        
        # Time to expiration
        dte = flow.get("dte", 0)
        if dte == 0:  # 0DTE
            score += 0.3
        elif dte <= 7:  # Weekly
            score += 0.2
        
        # Sweep order type
        if flow.get("order_type") == "sweep":
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_dark_pool_score(self, trade: Dict) -> float:
        """
        Calculate confidence score for dark pool signal.
        
        Args:
            trade: Dark pool trade data
            
        Returns:
            Confidence score between 0 and 1
        """
        score = 0.0
        
        # Trade size
        value = trade.get("value", 0)
        if value > 10000000:  # Very large trade
            score += 0.4
        elif value > 5000000:  # Large trade
            score += 0.3
        elif value > 1000000:  # Medium trade
            score += 0.2
        
        # Premium/discount
        if trade.get("premium_to_vwap", 0) > 0:
            score += 0.2
        
        # Trade type
        if trade.get("trade_type") == "block":
            score += 0.2
        
        # Recent price action correlation
        if trade.get("price_impact", 0) > 0:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_news_score(self, article: Dict) -> float:
        """
        Calculate sentiment score for news article.
        
        Args:
            article: News article data
            
        Returns:
            Sentiment score between -1 and 1
        """
        # TODO: Implement sentiment analysis using NLP
        # For now, return a neutral score
        return 0.0
    
    def _update_recommendations(self, symbol: str, signals: List[Dict]):
        """
        Update trade recommendations based on signals.
        
        Args:
            symbol: Stock symbol
            signals: List of trading signals
        """
        if self.trades_today >= self.max_trades_per_day:
            logger.info("Maximum daily trades reached")
            return
        
        # Calculate combined confidence score
        total_confidence = sum(signal["confidence"] for signal in signals)
        avg_confidence = total_confidence / len(signals)
        
        # Determine overall direction
        bullish_signals = sum(1 for s in signals if s["direction"] == "bullish")
        bearish_signals = sum(1 for s in signals if s["direction"] == "bearish")
        
        if bullish_signals > bearish_signals:
            direction = "bullish"
        elif bearish_signals > bullish_signals:
            direction = "bearish"
        else:
            direction = "neutral"
        
        # Create recommendation if confidence is high enough
        if avg_confidence > 0.7:  # High confidence threshold
            recommendation = {
                "symbol": symbol,
                "direction": direction,
                "confidence": avg_confidence,
                "signals": signals,
                "timestamp": datetime.now().isoformat(),
                "trade_type": "0DTE" if self.config["trading"]["zero_dte_only"] else "options"
            }
            
            self.last_recommendations.append(recommendation)
            self.trades_today += 1
            
            logger.info(f"New trade recommendation: {json.dumps(recommendation, indent=2)}")
    
    def get_recommendations(self, limit: int = 3) -> List[Dict]:
        """
        Get the latest trade recommendations.
        
        Args:
            limit: Maximum number of recommendations to return
            
        Returns:
            List of trade recommendations
        """
        return sorted(
            self.last_recommendations,
            key=lambda x: x["confidence"],
            reverse=True
        )[:limit]
    
    def reset_daily_counts(self):
        """Reset daily trade counts."""
        self.trades_today = 0
        self.last_recommendations = []


# Example usage
if __name__ == "__main__":
    # Initialize data fetcher
    data_fetcher = DataFetcher()
    data_fetcher.initialize()
    
    # Initialize scanner
    scanner = DeepSeekScanner(data_fetcher)
    
    # Start data fetcher
    data_fetcher.start()
    
    try:
        # Keep the script running
        while True:
            # Get latest recommendations
            recommendations = scanner.get_recommendations()
            if recommendations:
                print("\nLatest recommendations:")
                print(json.dumps(recommendations, indent=2))
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        # Stop data fetcher on keyboard interrupt
        data_fetcher.stop()
        print("Scanner stopped") 