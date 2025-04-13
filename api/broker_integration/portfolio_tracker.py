import logging
import json
import os
import csv
import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union

from .broker_interface import Position, Order, OrderSide
from .broker_manager import BrokerManager

logger = logging.getLogger(__name__)

class Trade:
    """Represents a completed trade with entry, exit, and performance metrics"""
    
    def __init__(
        self,
        trade_id: str,
        symbol: str,
        side: str,
        entry_date: datetime.datetime,
        entry_price: float,
        entry_order_id: str,
        qty: float,
        exit_date: Optional[datetime.datetime] = None,
        exit_price: Optional[float] = None,
        exit_order_id: Optional[str] = None,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
        commission: float = 0.0,
        strategy: str = "default",
        tags: List[str] = None,
        notes: str = "",
    ):
        self.trade_id = trade_id
        self.symbol = symbol
        self.side = side
        self.entry_date = entry_date
        self.entry_price = entry_price
        self.entry_order_id = entry_order_id
        self.qty = qty
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.exit_order_id = exit_order_id
        self.stop_loss_price = stop_loss_price
        self.take_profit_price = take_profit_price
        self.commission = commission
        self.strategy = strategy
        self.tags = tags or []
        self.notes = notes
        
        # Calculate PnL if we have exit information
        self.realized_pnl = 0.0
        self.realized_pnl_pct = 0.0
        
        if self.exit_price and self.entry_price:
            if self.side.lower() == "buy":
                self.realized_pnl = (self.exit_price - self.entry_price) * self.qty - self.commission
                self.realized_pnl_pct = ((self.exit_price / self.entry_price) - 1) * 100
            else:
                self.realized_pnl = (self.entry_price - self.exit_price) * self.qty - self.commission
                self.realized_pnl_pct = ((self.entry_price / self.exit_price) - 1) * 100
    
    @property
    def is_open(self) -> bool:
        """Check if the trade is still open"""
        return self.exit_date is None
    
    @property
    def duration(self) -> Optional[float]:
        """Get the duration of the trade in days"""
        if self.exit_date is None or self.entry_date is None:
            return None
        
        return (self.exit_date - self.entry_date).total_seconds() / 86400  # Convert seconds to days
    
    def update_exit(
        self,
        exit_date: datetime.datetime,
        exit_price: float,
        exit_order_id: str
    ):
        """Update the trade with exit information"""
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.exit_order_id = exit_order_id
        
        # Recalculate PnL
        if self.side.lower() == "buy":
            self.realized_pnl = (self.exit_price - self.entry_price) * self.qty - self.commission
            self.realized_pnl_pct = ((self.exit_price / self.entry_price) - 1) * 100
        else:
            self.realized_pnl = (self.entry_price - self.exit_price) * self.qty - self.commission
            self.realized_pnl_pct = ((self.entry_price / self.exit_price) - 1) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trade to dictionary for serialization"""
        return {
            "trade_id": self.trade_id,
            "symbol": self.symbol,
            "side": self.side,
            "entry_date": self.entry_date.isoformat() if self.entry_date else None,
            "entry_price": self.entry_price,
            "entry_order_id": self.entry_order_id,
            "qty": self.qty,
            "exit_date": self.exit_date.isoformat() if self.exit_date else None,
            "exit_price": self.exit_price,
            "exit_order_id": self.exit_order_id,
            "stop_loss_price": self.stop_loss_price,
            "take_profit_price": self.take_profit_price,
            "commission": self.commission,
            "strategy": self.strategy,
            "tags": self.tags,
            "notes": self.notes,
            "realized_pnl": self.realized_pnl,
            "realized_pnl_pct": self.realized_pnl_pct,
            "is_open": self.is_open,
            "duration": self.duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Trade':
        """Create a Trade object from a dictionary"""
        entry_date = datetime.datetime.fromisoformat(data["entry_date"]) if data.get("entry_date") else None
        exit_date = datetime.datetime.fromisoformat(data["exit_date"]) if data.get("exit_date") else None
        
        return cls(
            trade_id=data["trade_id"],
            symbol=data["symbol"],
            side=data["side"],
            entry_date=entry_date,
            entry_price=data["entry_price"],
            entry_order_id=data["entry_order_id"],
            qty=data["qty"],
            exit_date=exit_date,
            exit_price=data.get("exit_price"),
            exit_order_id=data.get("exit_order_id"),
            stop_loss_price=data.get("stop_loss_price"),
            take_profit_price=data.get("take_profit_price"),
            commission=data.get("commission", 0.0),
            strategy=data.get("strategy", "default"),
            tags=data.get("tags", []),
            notes=data.get("notes", "")
        )


class PerformanceMetrics:
    """Calculate and track performance metrics for a portfolio"""
    
    def __init__(self, trades: List[Trade] = None):
        self.trades = trades or []
        self.daily_pnl = {}  # Dictionary of date -> pnl for that day
        self.metrics = {}
        
        if trades:
            self.calculate_metrics()
    
    def add_trade(self, trade: Trade):
        """Add a trade and update metrics"""
        self.trades.append(trade)
        self.calculate_metrics()
    
    def calculate_metrics(self):
        """Calculate performance metrics from trades"""
        if not self.trades:
            self.metrics = {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "avg_profit": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0,
                "total_pnl": 0.0,
                "max_profit": 0.0,
                "max_loss": 0.0,
                "avg_trade_pnl": 0.0,
                "avg_trade_pnl_pct": 0.0,
                "total_commission": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "max_drawdown_pct": 0.0
            }
            return
        
        # Basic metrics
        closed_trades = [t for t in self.trades if not t.is_open]
        total_trades = len(closed_trades)
        
        if total_trades == 0:
            self.metrics = {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "avg_profit": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0,
                "total_pnl": 0.0,
                "max_profit": 0.0,
                "max_loss": 0.0,
                "avg_trade_pnl": 0.0,
                "avg_trade_pnl_pct": 0.0,
                "total_commission": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "max_drawdown_pct": 0.0
            }
            return
        
        winning_trades = [t for t in closed_trades if t.realized_pnl > 0]
        losing_trades = [t for t in closed_trades if t.realized_pnl <= 0]
        
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        
        # Win rate and PnL
        win_rate = win_count / total_trades if total_trades > 0 else 0.0
        
        # Calculate total, average, and max PnL
        total_pnl = sum(t.realized_pnl for t in closed_trades)
        avg_trade_pnl = total_pnl / total_trades if total_trades > 0 else 0.0
        avg_trade_pnl_pct = sum(t.realized_pnl_pct for t in closed_trades) / total_trades if total_trades > 0 else 0.0
        
        avg_profit = sum(t.realized_pnl for t in winning_trades) / win_count if win_count > 0 else 0.0
        avg_loss = sum(t.realized_pnl for t in losing_trades) / loss_count if loss_count > 0 else 0.0
        
        max_profit = max([t.realized_pnl for t in winning_trades]) if winning_trades else 0.0
        max_loss = min([t.realized_pnl for t in losing_trades]) if losing_trades else 0.0
        
        # Calculate profit factor (gross profit / gross loss)
        gross_profit = sum(t.realized_pnl for t in winning_trades)
        gross_loss = abs(sum(t.realized_pnl for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Calculate total commission
        total_commission = sum(t.commission for t in closed_trades)
        
        # Calculate daily PnL
        self._calculate_daily_pnl()
        
        # Calculate Sharpe ratio (assuming daily returns)
        daily_returns = list(self.daily_pnl.values())
        if daily_returns:
            avg_daily_return = np.mean(daily_returns)
            std_daily_return = np.std(daily_returns)
            sharpe_ratio = (avg_daily_return / std_daily_return) * np.sqrt(252) if std_daily_return > 0 else 0.0
        else:
            sharpe_ratio = 0.0
        
        # Calculate max drawdown
        max_drawdown, max_drawdown_pct = self._calculate_max_drawdown()
        
        # Store metrics
        self.metrics = {
            "total_trades": total_trades,
            "winning_trades": win_count,
            "losing_trades": loss_count,
            "win_rate": win_rate,
            "avg_profit": avg_profit,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "total_pnl": total_pnl,
            "max_profit": max_profit,
            "max_loss": max_loss,
            "avg_trade_pnl": avg_trade_pnl,
            "avg_trade_pnl_pct": avg_trade_pnl_pct,
            "total_commission": total_commission,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "max_drawdown_pct": max_drawdown_pct
        }
    
    def _calculate_daily_pnl(self):
        """Calculate daily PnL from trades"""
        self.daily_pnl = {}
        
        # Get all closed trades
        closed_trades = [t for t in self.trades if not t.is_open]
        
        # Group trades by exit date
        for trade in closed_trades:
            if trade.exit_date:
                date_key = trade.exit_date.date().isoformat()
                if date_key in self.daily_pnl:
                    self.daily_pnl[date_key] += trade.realized_pnl
                else:
                    self.daily_pnl[date_key] = trade.realized_pnl
    
    def _calculate_max_drawdown(self) -> tuple:
        """Calculate the maximum drawdown from daily PnL"""
        if not self.daily_pnl:
            return 0.0, 0.0
        
        # Sort daily PnL by date
        sorted_daily_pnl = sorted(
            [(datetime.date.fromisoformat(date), pnl) for date, pnl in self.daily_pnl.items()],
            key=lambda x: x[0]
        )
        
        # Calculate cumulative PnL
        cumulative_pnl = []
        current_pnl = 0.0
        for _, pnl in sorted_daily_pnl:
            current_pnl += pnl
            cumulative_pnl.append(current_pnl)
        
        # Calculate drawdown
        max_dd = 0.0
        max_dd_pct = 0.0
        peak = cumulative_pnl[0]
        
        for pnl in cumulative_pnl:
            if pnl > peak:
                peak = pnl
            
            dd = peak - pnl
            dd_pct = (dd / peak) * 100 if peak > 0 else 0.0
            
            max_dd = max(max_dd, dd)
            max_dd_pct = max(max_dd_pct, dd_pct)
        
        return max_dd, max_dd_pct
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return self.metrics
    
    def get_daily_pnl(self) -> Dict[str, float]:
        """Get daily PnL"""
        return self.daily_pnl


class PortfolioTracker:
    """Track portfolio performance and trade history"""
    
    def __init__(self, broker_manager: BrokerManager, trades_file: str = "trade_history.json"):
        """Initialize the portfolio tracker with a broker manager"""
        self.broker_manager = broker_manager
        self.trades_file = trades_file
        self.trades: Dict[str, Trade] = {}
        self.performance = PerformanceMetrics()
        
        # Load trade history if file exists
        self._load_trades()
    
    def _load_trades(self):
        """Load trades from JSON file"""
        if os.path.exists(self.trades_file):
            try:
                with open(self.trades_file, "r") as f:
                    trade_data = json.load(f)
                
                for trade_id, trade_info in trade_data.items():
                    self.trades[trade_id] = Trade.from_dict(trade_info)
                
                # Update performance metrics
                self.performance = PerformanceMetrics(list(self.trades.values()))
                
                logger.info(f"Loaded {len(self.trades)} trades from {self.trades_file}")
            except Exception as e:
                logger.error(f"Error loading trades from {self.trades_file}: {e}")
    
    def _save_trades(self):
        """Save trades to JSON file"""
        try:
            trade_data = {
                trade_id: trade.to_dict()
                for trade_id, trade in self.trades.items()
            }
            
            with open(self.trades_file, "w") as f:
                json.dump(trade_data, f, indent=4)
            
            logger.info(f"Saved {len(self.trades)} trades to {self.trades_file}")
        except Exception as e:
            logger.error(f"Error saving trades to {self.trades_file}: {e}")
    
    def add_trade(self, trade: Trade):
        """Add a new trade to the tracker"""
        self.trades[trade.trade_id] = trade
        self.performance.add_trade(trade)
        self._save_trades()
    
    def update_trade(self, trade_id: str, **kwargs):
        """Update an existing trade with new information"""
        if trade_id not in self.trades:
            logger.error(f"Trade {trade_id} not found")
            return False
        
        trade = self.trades[trade_id]
        
        # Handle exit information specifically
        if "exit_date" in kwargs and "exit_price" in kwargs and "exit_order_id" in kwargs:
            trade.update_exit(
                exit_date=kwargs["exit_date"],
                exit_price=kwargs["exit_price"],
                exit_order_id=kwargs["exit_order_id"]
            )
        
        # Update other attributes
        for key, value in kwargs.items():
            if key not in ["exit_date", "exit_price", "exit_order_id"] and hasattr(trade, key):
                setattr(trade, key, value)
        
        # Update performance metrics
        self.performance = PerformanceMetrics(list(self.trades.values()))
        
        # Save updated trades
        self._save_trades()
        
        return True
    
    def get_trade(self, trade_id: str) -> Optional[Trade]:
        """Get a specific trade by ID"""
        return self.trades.get(trade_id)
    
    def get_trades(self, symbol: Optional[str] = None, is_open: Optional[bool] = None) -> List[Trade]:
        """Get trades with optional filtering"""
        trades = list(self.trades.values())
        
        if symbol:
            trades = [t for t in trades if t.symbol == symbol]
        
        if is_open is not None:
            trades = [t for t in trades if t.is_open == is_open]
        
        return trades
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return self.performance.get_metrics()
    
    def get_daily_pnl(self) -> Dict[str, float]:
        """Get daily PnL"""
        return self.performance.get_daily_pnl()
    
    def export_trades_to_csv(self, filepath: str):
        """Export trades to CSV file"""
        try:
            trades_list = [trade.to_dict() for trade in self.trades.values()]
            df = pd.DataFrame(trades_list)
            df.to_csv(filepath, index=False)
            logger.info(f"Exported {len(trades_list)} trades to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting trades to CSV: {e}")
            return False
    
    def sync_with_broker(self):
        """Sync local trade records with broker's data"""
        try:
            # This requires a more sophisticated implementation
            # to match broker trades with local records
            broker = self.broker_manager.get_broker()
            
            # Get closed positions from broker
            orders = broker.get_orders()
            
            # TODO: Match orders with existing trades and
            # update open trades with final execution data
            
            logger.info("Synced trades with broker")
            return True
        except Exception as e:
            logger.error(f"Error syncing with broker: {e}")
            return False 