"""
Alpaca broker implementation.

This module implements the BrokerInterface for the Alpaca trading API.
"""

import os
import logging
from datetime import datetime, timedelta
import time
import threading
import random
import pandas as pd
from typing import Dict, List, Optional, Any, Union
import json
import importlib
import uuid

from .broker_interface import (
    BrokerInterface,
    Account,
    Position,
    Order,
    OrderStatus,
    OrderSide,
    OrderType,
    TimeInForce
)
from .mock_broker import MockBroker
from .alpaca import AlpacaBroker as NewAlpacaBroker
try:
    from api.config import bot_config
except ImportError:
    # Fallback to a direct import if the module-relative import fails
    try:
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from api.config import bot_config
    except ImportError:
        logger = logging.getLogger(__name__)
        logger.warning("Could not import bot_config, using default configuration")
        bot_config = {}

import alpaca_trade_api as tradeapi
from alpaca_trade_api.entity import Order as AlpacaOrder
from alpaca_trade_api.entity import Position as AlpacaPosition
from alpaca_trade_api.entity import Account as AlpacaAccount
from alpaca_trade_api.rest import APIError

logger = logging.getLogger(__name__)

# Mappings from Alpaca API values to our enum values
ALPACA_STATUS_MAP = {
    "new": OrderStatus.NEW,
    "filled": OrderStatus.FILLED,
    "partially_filled": OrderStatus.PARTIALLY_FILLED,
    "canceled": OrderStatus.CANCELLED,
    "expired": OrderStatus.EXPIRED,
    "rejected": OrderStatus.REJECTED,
    "done_for_day": OrderStatus.DONE_FOR_DAY,
    "pending_cancel": OrderStatus.PENDING_CANCEL,
    "pending_replace": OrderStatus.PENDING_REPLACE,
}

ALPACA_SIDE_MAP = {
    "buy": OrderSide.BUY,
    "sell": OrderSide.SELL,
}

ALPACA_TYPE_MAP = {
    "market": OrderType.MARKET,
    "limit": OrderType.LIMIT,
    "stop": OrderType.STOP,
    "stop_limit": OrderType.STOP_LIMIT,
}

ALPACA_TIF_MAP = {
    "day": TimeInForce.DAY,
    "gtc": TimeInForce.GTC,
    "opg": TimeInForce.OPG,
    "cls": TimeInForce.CLS,
    "ioc": TimeInForce.IOC,
    "fok": TimeInForce.FOK,
}

# Reverse mappings (our enum values to Alpaca API values)
REVERSE_STATUS_MAP = {v: k for k, v in ALPACA_STATUS_MAP.items()}
REVERSE_SIDE_MAP = {v: k for k, v in ALPACA_SIDE_MAP.items()}
REVERSE_TYPE_MAP = {v: k for k, v in ALPACA_TYPE_MAP.items()}
REVERSE_TIF_MAP = {v: k for k, v in ALPACA_TIF_MAP.items()}

class AlpacaBroker(BrokerInterface):
    """Alpaca broker implementation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Alpaca broker with configuration"""
        self.config = config or {}
        self.api_key = self.config.get("api_key", "")
        self.api_secret = self.config.get("api_secret", "")
        self.is_paper = self.config.get("is_paper", True)
        self.base_url = self.config.get("base_url", "https://paper-api.alpaca.markets" if self.is_paper else "https://api.alpaca.markets")
        
        self.connected = False
        self.api = None  # Will hold the Alpaca API client
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate broker configuration"""
        if not self.api_key or not self.api_secret:
            logger.warning("Missing Alpaca API credentials")
    
    def connect(self) -> bool:
        """Connect to Alpaca API"""
        if not self.api_key or not self.api_secret:
            logger.error("Cannot connect to Alpaca: missing API credentials")
            return False
        
        try:
            # In a real implementation, we would initialize the Alpaca API client here
            # For now, we'll simulate a successful connection
            self.connected = True
            logger.info("Connected to Alpaca API")
                return True
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca API: {e}")
            self.connected = False
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Alpaca API"""
        self.connected = False
        logger.info("Disconnected from Alpaca API")
            return True
    
    def is_connected(self) -> bool:
        """Check if connected to Alpaca API"""
        return self.connected
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        if not self.is_connected():
            logger.error("Not connected to Alpaca API")
            return {
                "error": "Not connected to Alpaca API",
                "status": "error"
            }
        
        try:
            # In a real implementation, we would call the Alpaca API here
            # For now, we'll return a mock account
            return {
                "id": "alpaca-account-id",
                "cash": 100000.0,
                "portfolio_value": 110000.0,
                "buying_power": 200000.0,
                "equity": 110000.0,
                "currency": "USD"
            }
        except Exception as e:
            logger.error(f"Error getting account info from Alpaca: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all positions"""
        if not self.is_connected():
            logger.error("Not connected to Alpaca API")
            return []
        
        try:
            # In a real implementation, we would call the Alpaca API here
            # For now, we'll return mock positions
            return [
                {
                    "symbol": "AAPL",
                    "qty": 10,
                    "avg_entry_price": 150.0,
                    "current_price": 155.0,
                    "market_value": 1550.0,
                    "unrealized_pl": 50.0,
                    "unrealized_pl_percent": 3.33,
                    "side": "buy"
                },
                {
                    "symbol": "MSFT",
                    "qty": 5,
                    "avg_entry_price": 300.0,
                    "current_price": 310.0,
                    "market_value": 1550.0,
                    "unrealized_pl": 50.0,
                    "unrealized_pl_percent": 3.33,
                    "side": "buy"
                }
            ]
        except Exception as e:
            logger.error(f"Error getting positions from Alpaca: {e}")
            return []
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get position for a specific symbol"""
        if not self.is_connected():
            logger.error("Not connected to Alpaca API")
            return None
        
        try:
            # In a real implementation, we would call the Alpaca API here
            # For now, we'll return a mock position if symbol matches sample data
            positions = self.get_positions()
            for position in positions:
                if position["symbol"].upper() == symbol.upper():
                    return position
            return None
        except Exception as e:
            logger.error(f"Error getting position for {symbol} from Alpaca: {e}")
            return None
    
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get orders with optional status filter"""
        if not self.is_connected():
            logger.error("Not connected to Alpaca API")
            return []
        
        try:
            # In a real implementation, we would call the Alpaca API here
            # For now, we'll return mock orders
            orders = [
                {
                    "id": "alpaca-order-1",
                    "symbol": "AAPL",
                    "qty": 10,
                    "side": "buy",
                    "type": "market",
                    "status": "filled",
                    "created_at": datetime.now().isoformat(),
                    "filled_at": datetime.now().isoformat(),
                    "filled_qty": 10,
                    "filled_avg_price": 150.0
                },
                {
                    "id": "alpaca-order-2",
                    "symbol": "MSFT",
                    "qty": 5,
                    "side": "buy",
                    "type": "limit",
                    "limit_price": 300.0,
                    "status": "new",
                    "created_at": datetime.now().isoformat(),
                    "filled_qty": 0
                }
            ]
            
            # Filter by status if provided
            if status:
                return [o for o in orders if o["status"] == status]
            return orders
        except Exception as e:
            logger.error(f"Error getting orders from Alpaca: {e}")
            return []
    
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific order by ID"""
        if not self.is_connected():
            logger.error("Not connected to Alpaca API")
            return None
        
        try:
            # In a real implementation, we would call the Alpaca API here
            # For now, we'll return a mock order if ID matches sample data
            orders = self.get_orders()
            for order in orders:
                if order["id"] == order_id:
                    return order
            return None
        except Exception as e:
            logger.error(f"Error getting order {order_id} from Alpaca: {e}")
            return None
    
    def place_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        type: str = "market",
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "day"
    ) -> Dict[str, Any]:
        """Place an order with Alpaca"""
        if not self.is_connected():
            logger.error("Not connected to Alpaca API")
            return {
                "error": "Not connected to Alpaca API",
                "status": "rejected"
            }
        
        try:
            # In a real implementation, we would call the Alpaca API here
            # For now, we'll return a mock order
            import uuid
            
            order_id = f"alpaca-{uuid.uuid4()}"
            
            order = {
                "id": order_id,
                "symbol": symbol.upper(),
                "qty": qty,
                "side": side,
                "type": type,
                "time_in_force": time_in_force,
                "status": "new",
                "created_at": datetime.now().isoformat(),
                "filled_qty": 0
            }
            
            if limit_price is not None:
                order["limit_price"] = limit_price
            
            if stop_price is not None:
                order["stop_price"] = stop_price
            
            logger.info(f"Placed order with Alpaca: {order_id}")
            return order
        except Exception as e:
            logger.error(f"Error placing order with Alpaca: {e}")
            return {
                "error": str(e),
                "status": "rejected"
            }
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order with Alpaca"""
        if not self.is_connected():
            logger.error("Not connected to Alpaca API")
            return False
        
        try:
            # In a real implementation, we would call the Alpaca API here
            # For now, we'll simulate a successful cancellation
            logger.info(f"Cancelled order with Alpaca: {order_id}")
                return True
        except Exception as e:
            logger.error(f"Error cancelling order with Alpaca: {e}")
            return False
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get market data for a symbol from Alpaca"""
        if not self.is_connected():
            logger.error("Not connected to Alpaca API")
            return {
                "error": "Not connected to Alpaca API",
                "symbol": symbol
            }
        
        try:
            # In a real implementation, we would call the Alpaca API here
            # For now, we'll return mock market data
            return {
                "symbol": symbol.upper(),
                "last_price": 155.0,
                "bid": 154.9,
                "ask": 155.1,
                "volume": 1000000,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting market data for {symbol} from Alpaca: {e}")
            return {
                "error": str(e),
                "symbol": symbol
            }
    
    def get_bot_status(self) -> bool:
        """Get status of the trading bot"""
        return self.is_running
    
    def start_bot(self) -> bool:
        """Start the trading bot"""
        if self.is_running:
            logger.warning("Bot is already running")
                return True
            
        try:
                self.stop_event.clear()
                self.trading_thread = threading.Thread(target=self._trading_loop)
                self.trading_thread.daemon = True
                self.trading_thread.start()
            self.is_running = True
            logger.info("Bot started successfully")
                    return True
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            return False
    
    def stop_bot(self) -> bool:
        """Stop the trading bot"""
        if not self.is_running:
            logger.warning("Bot is not running")
                return True
            
        try:
                self.stop_event.set()
                if self.trading_thread and self.trading_thread.is_alive():
                self.trading_thread.join(timeout=5.0)
            self.is_running = False
            logger.info("Bot stopped successfully")
                    return True
        except Exception as e:
            logger.error(f"Failed to stop bot: {e}")
            return False
    
    def _trading_loop(self) -> None:
        """Main trading loop"""
        logger.info("Trading loop started")
        while not self.stop_event.is_set():
            try:
                self.run_trading_cycle()
            except Exception as e:
                logger.error(f"Error in trading cycle: {e}")
            
            # Sleep for a bit
            time.sleep(60)  # 1 minute
        
        logger.info("Trading loop ended")
    
    def run_trading_cycle(self) -> bool:
        """Run a single trading cycle"""
        try:
            # Make sure we're connected
            self._ensure_connected()
            
            # Update prices
            self._update_active_trade_prices()
            
            # Check for exit conditions
            self._check_exit_conditions()
            
            # Look for new trades
            self._find_new_trades()
            
            # Update portfolio performance
            self._update_portfolio_performance()
            
                return True
        except Exception as e:
            logger.error(f"Error running trading cycle: {e}")
            return False
    
    def get_active_trades(self) -> List[Dict[str, Any]]:
        """Get list of active trades"""
        try:
            if os.path.exists(self.active_trades_file):
                with open(self.active_trades_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error getting active trades: {e}")
            return []
    
    def get_trading_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get trading history"""
        try:
            if os.path.exists(self.trade_history_file):
                with open(self.trade_history_file, 'r') as f:
                    trades = json.load(f)
                    
                if limit and limit > 0:
                    return trades[-limit:]
                return trades
            return []
        except Exception as e:
            logger.error(f"Error getting trading history: {e}")
            return []
    
    def get_real_time_data(self) -> Dict[str, Any]:
        """Get real-time data for the dashboard"""
        positions = self.get_positions()
        account = self.get_account_info()
        active_trades = self.get_active_trades()
        
        # Get market data for positions
        position_data = []
        for pos in positions:
            try:
                market_data = self.get_market_data(pos["symbol"])
                
                position_data.append({
                    "symbol": pos["symbol"],
                    "quantity": pos["qty"],
                    "avg_price": pos["avg_entry_price"],
                    "current_price": market_data["last_price"],
                    "value": pos["qty"] * market_data["last_price"],
                    "profit_loss": (market_data["last_price"] - pos["avg_entry_price"]) * pos["qty"],
                    "profit_loss_pct": ((market_data["last_price"] / pos["avg_entry_price"]) - 1) * 100 if pos["avg_entry_price"] > 0 else 0,
                    "day_change": random.uniform(-5, 5),  # Mock data
                    "day_change_pct": random.uniform(-3, 3),  # Mock data
                })
            except Exception as e:
                logger.error(f"Error processing position data for {pos['symbol']}: {e}")
        
        # Add some mock market data for common indices
        market_indices = ["SPY", "QQQ", "DIA", "IWM"]
        market_overview = []
        
        for symbol in market_indices:
            self._add_mock_data(market_overview, symbol)
        
        # Add some mock sector data
        sectors = ["XLF", "XLK", "XLE", "XLV", "XLI", "XLP", "XLY", "XLU", "XLB", "XLRE"]
        sector_performance = []
        
        for symbol in sectors:
            self._add_mock_data(sector_performance, symbol)
            
            return {
            "account": {
                "equity": account["equity"],
                "cash": account["cash"],
                "buying_power": account["buying_power"],
                "day_pl": random.uniform(-1000, 1000),  # Mock data
                "day_pl_pct": random.uniform(-2, 2),  # Mock data
                "total_pl": random.uniform(-2000, 5000),  # Mock data
                "total_pl_pct": random.uniform(-10, 20),  # Mock data
            },
            "positions": position_data,
            "active_trades": active_trades,
            "market_overview": market_overview,
            "sector_performance": sector_performance,
            "last_update": datetime.now().isoformat()
            }
    
    def _add_mock_data(self, data_dict: Dict[str, Any], symbol: str) -> None:
        """Add mock market data for a symbol"""
        price = random.uniform(100, 500)
        change = random.uniform(-5, 5)
        change_pct = (change / price) * 100
        
        data_dict.append({
            "symbol": symbol,
            "price": price,
            "change": change,
            "change_pct": change_pct,
            "volume": random.randint(1000000, 10000000)
        })
    
    def _update_active_trade_prices(self) -> None:
        """Update prices for active trades"""
        try:
            active_trades = self.get_active_trades()
            if not active_trades:
                return
                
            updated = False
            
            for trade in active_trades:
                try:
                    symbol = trade.get("symbol")
                    if not symbol:
                        continue
                        
                    # Get current price
                    market_data = self.get_market_data(symbol)
                    current_price = market_data["last_price"]
                    
                    if current_price <= 0:
                        continue
                        
                    # Update trade data
                    entry_price = trade.get("avg_entry_price", 0)
                    quantity = trade.get("qty", 0)
                    
                    if entry_price <= 0 or quantity <= 0:
                        continue
                        
                    # Calculate P&L
                    if trade.get("side") == "buy":
                        profit_loss = (current_price - entry_price) * quantity
                        profit_loss_pct = ((current_price / entry_price) - 1) * 100 if entry_price > 0 else 0
                    else:  # sell/short
                        profit_loss = (entry_price - current_price) * quantity
                        profit_loss_pct = ((entry_price / current_price) - 1) * 100 if current_price > 0 else 0
                    
                    # Update trade
                    trade["current_price"] = current_price
                    trade["profit_loss"] = profit_loss
                    trade["profit_loss_pct"] = profit_loss_pct
                    trade["last_update"] = datetime.now().isoformat()
                    
                    updated = True
                except Exception as e:
                    logger.error(f"Error updating trade prices for {trade.get('symbol')}: {e}")
                    
                    # Save updated trades
            if updated:
                with open(self.active_trades_file, 'w') as f:
                    json.dump(active_trades, f, indent=2)
        except Exception as e:
            logger.error(f"Error updating active trade prices: {e}")
    
    def _check_exit_conditions(self) -> None:
        """Check exit conditions for active trades"""
        try:
            active_trades = self.get_active_trades()
            if not active_trades:
                return
                
                    trades_to_close = []
            remaining_trades = []
            
            for trade in active_trades:
                try:
                    symbol = trade.get("symbol")
                    current_price = trade.get("current_price", 0)
                    
                    if current_price <= 0:
                        remaining_trades.append(trade)
                        continue
                    
                    stop_loss = trade.get("stop_loss")
                    take_profit = trade.get("take_profit")
                    
                    # Check if we need to exit the trade
                    exit_type = None
                    
                    if trade.get("side") == "buy":
                        # Long position
                        if stop_loss and current_price <= stop_loss:
                            exit_type = "stop_loss"
                        elif take_profit and current_price >= take_profit:
                            exit_type = "take_profit"
                    else:
                        # Short position
                        if stop_loss and current_price >= stop_loss:
                            exit_type = "stop_loss"
                        elif take_profit and current_price <= take_profit:
                            exit_type = "take_profit"
                    
                    if exit_type:
                        trade["exit_type"] = exit_type
                        trade["exit_price"] = current_price
                        trade["exit_date"] = datetime.now().isoformat()
                        
                        # Calculate final P&L
                        entry_price = trade.get("avg_entry_price", 0)
                        quantity = trade.get("qty", 0)
                        
                        if trade.get("side") == "buy":
                            profit_loss = (current_price - entry_price) * quantity
                            profit_loss_pct = ((current_price / entry_price) - 1) * 100 if entry_price > 0 else 0
                        else:  # sell/short
                            profit_loss = (entry_price - current_price) * quantity
                            profit_loss_pct = ((entry_price / current_price) - 1) * 100 if current_price > 0 else 0
                        
                        trade["final_profit_loss"] = profit_loss
                        trade["final_profit_loss_pct"] = profit_loss_pct
                        
                        # Add to trades to close
                        trades_to_close.append(trade)
                        
                        # Try to close the position
                        try:
                            side = OrderSide.SELL if trade.get("side") == "buy" else OrderSide.BUY
                            self.place_order(
                                symbol=symbol,
                                qty=quantity,
                                side=side,
                                type="market"
                            )
                            logger.info(f"Closed position for {symbol} - {exit_type}")
        except Exception as e:
                            logger.error(f"Error closing position for {symbol}: {e}")
            else:
                        remaining_trades.append(trade)
                except Exception as e:
                    logger.error(f"Error checking exit conditions for {trade.get('symbol')}: {e}")
                    remaining_trades.append(trade)
            
            # Update active trades file
            with open(self.active_trades_file, 'w') as f:
                json.dump(remaining_trades, f, indent=2)
                
            # Add closed trades to history
            if trades_to_close:
                history = self.get_trading_history()
                history.extend(trades_to_close)
                
                with open(self.trade_history_file, 'w') as f:
                    json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Error checking exit conditions: {e}")
    
    def _find_new_trades(self) -> None:
        """Find new trading opportunities"""
        # This is a placeholder. In a real implementation, you would:
        # 1. Run your trading strategy models
        # 2. Analyze market conditions
        # 3. Find entry points
        # 4. Submit orders for new trades
        pass
    
    def _update_portfolio_performance(self) -> None:
        """Update portfolio performance metrics"""
        # This is a placeholder. In a real implementation, you would:
        # 1. Calculate daily and overall performance
        # 2. Update performance tracking data
        # 3. Generate performance reports
        pass

    def cancel_all_orders(self) -> bool:
        """Cancel all open orders with Alpaca"""
        if not self.is_connected():
            logger.error("Not connected to Alpaca API")
            return False
        
        try:
            # In a real implementation, we would call the Alpaca API here
            # For now, we'll simulate a successful cancellation of all orders
            logger.info("Cancelled all orders with Alpaca")
                return True
        except Exception as e:
            logger.error(f"Error cancelling all orders with Alpaca: {e}")
            return False 
