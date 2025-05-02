import logging
import json
import os
import csv
import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union, NamedTuple
import uuid

from .broker_interface import Position, Order, OrderSide
from .broker_manager import BrokerManager

logger = logging.getLogger(__name__)

class Trade(NamedTuple):
    """Represents a complete trade (entry and exit)"""
    id: str
    symbol: str
    entry_date: datetime.datetime
    exit_date: Optional[datetime.datetime]
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    side: str  # "long" or "short"
    strategy: str
    pnl: Optional[float]
    pnl_percent: Optional[float]
    fees: float
    status: str  # "open" or "closed"
    entry_order_id: Optional[str]
    exit_order_id: Optional[str]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    notes: Optional[str]
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "entry_date": self.entry_date.isoformat() if self.entry_date else None,
            "exit_date": self.exit_date.isoformat() if self.exit_date else None,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "quantity": self.quantity,
            "side": self.side,
            "strategy": self.strategy,
            "pnl": self.pnl,
            "pnl_percent": self.pnl_percent,
            "fees": self.fees,
            "status": self.status,
            "entry_order_id": self.entry_order_id,
            "exit_order_id": self.exit_order_id,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "notes": self.notes,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Trade':
        """Create a Trade from dictionary"""
        entry_date = datetime.datetime.fromisoformat(data["entry_date"]) if data.get("entry_date") else None
        exit_date = datetime.datetime.fromisoformat(data["exit_date"]) if data.get("exit_date") else None
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            symbol=data.get("symbol", ""),
            entry_date=entry_date,
            exit_date=exit_date,
            entry_price=data.get("entry_price", 0.0),
            exit_price=data.get("exit_price"),
            quantity=data.get("quantity", 0.0),
            side=data.get("side", "long"),
            strategy=data.get("strategy", ""),
            pnl=data.get("pnl"),
            pnl_percent=data.get("pnl_percent"),
            fees=data.get("fees", 0.0),
            status=data.get("status", "open"),
            entry_order_id=data.get("entry_order_id"),
            exit_order_id=data.get("exit_order_id"),
            stop_loss=data.get("stop_loss"),
            take_profit=data.get("take_profit"),
            notes=data.get("notes"),
            tags=data.get("tags", [])
        )

class PerformanceMetrics:
    """Performance metrics for a trading account"""
    
    def __init__(self, trades: List[Trade], starting_balance: float = 10000.0):
        self.trades = trades
        self.starting_balance = starting_balance
        
        # Cache computed metrics
        self._win_rate = None
        self._profit_factor = None
        self._max_drawdown = None
        self._avg_win = None
        self._avg_loss = None
        self._sharpe_ratio = None
    
    @property
    def total_trades(self) -> int:
        """Total number of closed trades"""
        return len([t for t in self.trades if t.status == "closed"])
    
    @property
    def winning_trades(self) -> int:
        """Number of winning trades"""
        return len([t for t in self.trades if t.status == "closed" and t.pnl and t.pnl > 0])
    
    @property
    def losing_trades(self) -> int:
        """Number of losing trades"""
        return len([t for t in self.trades if t.status == "closed" and t.pnl and t.pnl < 0])
    
    @property
    def win_rate(self) -> float:
        """Win rate as a percentage"""
        if self._win_rate is not None:
            return self._win_rate
            
        if self.total_trades == 0:
            self._win_rate = 0.0
        else:
            self._win_rate = (self.winning_trades / self.total_trades) * 100
        
        return self._win_rate
    
    @property
    def gross_profit(self) -> float:
        """Sum of all winning trades"""
        return sum([t.pnl for t in self.trades if t.status == "closed" and t.pnl and t.pnl > 0])
    
    @property
    def gross_loss(self) -> float:
        """Sum of all losing trades (as a positive number)"""
        return abs(sum([t.pnl for t in self.trades if t.status == "closed" and t.pnl and t.pnl < 0]))
    
    @property
    def profit_factor(self) -> float:
        """Ratio of gross profit to gross loss"""
        if self._profit_factor is not None:
            return self._profit_factor
            
        if self.gross_loss == 0:
            if self.gross_profit > 0:
                self._profit_factor = float('inf')  # Perfect trading!
            else:
                self._profit_factor = 0.0
        else:
            self._profit_factor = self.gross_profit / self.gross_loss
        
        return self._profit_factor
    
    @property
    def net_profit(self) -> float:
        """Net profit across all trades"""
        return sum([t.pnl for t in self.trades if t.status == "closed" and t.pnl is not None])
    
    @property
    def net_profit_percent(self) -> float:
        """Net profit as a percentage of starting balance"""
        return (self.net_profit / self.starting_balance) * 100 if self.starting_balance > 0 else 0
    
    @property
    def average_win(self) -> float:
        """Average winning trade size"""
        if self._avg_win is not None:
            return self._avg_win
            
        if self.winning_trades == 0:
            self._avg_win = 0.0
        else:
            self._avg_win = self.gross_profit / self.winning_trades
        
        return self._avg_win
    
    @property
    def average_loss(self) -> float:
        """Average losing trade size (as a positive number)"""
        if self._avg_loss is not None:
            return self._avg_loss
            
        if self.losing_trades == 0:
            self._avg_loss = 0.0
        else:
            self._avg_loss = self.gross_loss / self.losing_trades
        
        return self._avg_loss
    
    @property
    def max_drawdown(self) -> float:
        """Maximum drawdown percentage"""
        if self._max_drawdown is not None:
            return self._max_drawdown
            
        # Sort trades by date
        sorted_trades = sorted([t for t in self.trades if t.status == "closed"], 
                               key=lambda x: x.exit_date or datetime.datetime.min)
        
        if not sorted_trades:
            self._max_drawdown = 0.0
            return self._max_drawdown
        
        # Calculate equity curve
        equity = self.starting_balance
        peak = equity
        drawdown = 0.0
        
        for trade in sorted_trades:
            if trade.pnl is not None:
                equity += trade.pnl
                
                if equity > peak:
                    peak = equity
                
                if peak > 0:  # Avoid division by zero
                    current_drawdown = (peak - equity) / peak * 100
                    drawdown = max(drawdown, current_drawdown)
        
        self._max_drawdown = drawdown
        return self._max_drawdown
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.win_rate,
            "gross_profit": self.gross_profit,
            "gross_loss": self.gross_loss,
            "profit_factor": self.profit_factor,
            "net_profit": self.net_profit,
            "net_profit_percent": self.net_profit_percent,
            "average_win": self.average_win,
            "average_loss": self.average_loss,
            "max_drawdown": self.max_drawdown
        }

class PortfolioTracker:
    """Tracks trades and portfolio performance"""
    
    def __init__(self, broker_manager: BrokerManager, trades_file: str = "trade_history.json"):
        self.broker_manager = broker_manager
        self.trades_file = trades_file
        self.trades: Dict[str, Trade] = {}
        
        # Load existing trades if file exists
        self.load_trades()
    
    def load_trades(self) -> None:
        """Load trades from file"""
        if os.path.exists(self.trades_file):
            try:
                with open(self.trades_file, 'r') as f:
                    trades_data = json.load(f)
                    for trade_data in trades_data:
                        trade = Trade.from_dict(trade_data)
                        self.trades[trade.id] = trade
                logger.info(f"Loaded {len(self.trades)} trades from {self.trades_file}")
            except Exception as e:
                logger.error(f"Error loading trades: {e}")
    
    def save_trades(self) -> None:
        """Save trades to file"""
        try:
            with open(self.trades_file, 'w') as f:
                json.dump([t.to_dict() for t in self.trades.values()], f, indent=2)
            logger.info(f"Saved {len(self.trades)} trades to {self.trades_file}")
        except Exception as e:
            logger.error(f"Error saving trades: {e}")
    
    def open_trade(
        self,
        symbol: str,
        quantity: float,
        entry_price: float,
        side: str,
        strategy: str,
        entry_order_id: Optional[str] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        fees: float = 0.0,
        notes: Optional[str] = None,
        tags: List[str] = None
    ) -> Trade:
        """
        Open a new trade
        
        Args:
            symbol: Trading symbol
            quantity: Number of shares/contracts/units
            entry_price: Entry price per share
            side: "long" or "short"
            strategy: Strategy name
            entry_order_id: Optional broker order ID
            stop_loss: Optional stop loss price
            take_profit: Optional take profit price
            fees: Trading fees
            notes: Optional notes
            tags: Optional list of tags
            
        Returns:
            The created Trade object
        """
        trade_id = str(uuid.uuid4())
        
        trade = Trade(
            id=trade_id,
            symbol=symbol,
            entry_date=datetime.datetime.now(),
            exit_date=None,
            entry_price=entry_price,
            exit_price=None,
            quantity=quantity,
            side=side,
            strategy=strategy,
            pnl=None,
            pnl_percent=None,
            fees=fees,
            status="open",
            entry_order_id=entry_order_id,
            exit_order_id=None,
            stop_loss=stop_loss,
            take_profit=take_profit,
            notes=notes,
            tags=tags or []
        )
        
        self.trades[trade_id] = trade
        self.save_trades()
        
        logger.info(f"Opened new {side} trade for {quantity} {symbol} at ${entry_price}")
        return trade
    
    def close_trade(
        self,
        trade_id: str,
        exit_price: float,
        exit_date: Optional[datetime.datetime] = None,
        exit_order_id: Optional[str] = None,
        fees: Optional[float] = None,
        notes: Optional[str] = None
    ) -> Optional[Trade]:
        """
        Close an existing trade
        
        Args:
            trade_id: ID of the trade to close
            exit_price: Exit price per share
            exit_date: Optional exit date (defaults to now)
            exit_order_id: Optional broker order ID
            fees: Optional additional fees
            notes: Optional notes to append
            
        Returns:
            Updated Trade object or None if trade not found
        """
        if trade_id not in self.trades:
            logger.error(f"Trade {trade_id} not found")
            return None
        
        trade = self.trades[trade_id]
        
        # Can't close an already closed trade
        if trade.status == "closed":
            logger.warning(f"Trade {trade_id} is already closed")
            return trade
        
        # Update trade with exit information
        exit_dt = exit_date or datetime.datetime.now()
        
        # Calculate P&L
        if trade.side == "long":
            pnl = (exit_price - trade.entry_price) * trade.quantity - (trade.fees + (fees or 0))
            pnl_percent = ((exit_price / trade.entry_price) - 1) * 100
        else:  # short
            pnl = (trade.entry_price - exit_price) * trade.quantity - (trade.fees + (fees or 0))
            pnl_percent = ((trade.entry_price / exit_price) - 1) * 100
        
        total_fees = trade.fees + (fees or 0)
        
        # Create updated trade
        updated_trade = Trade(
            id=trade.id,
            symbol=trade.symbol,
            entry_date=trade.entry_date,
            exit_date=exit_dt,
            entry_price=trade.entry_price,
            exit_price=exit_price,
            quantity=trade.quantity,
            side=trade.side,
            strategy=trade.strategy,
            pnl=pnl,
            pnl_percent=pnl_percent,
            fees=total_fees,
            status="closed",
            entry_order_id=trade.entry_order_id,
            exit_order_id=exit_order_id,
            stop_loss=trade.stop_loss,
            take_profit=trade.take_profit,
            notes=notes if notes else trade.notes,
            tags=trade.tags
        )
        
        self.trades[trade_id] = updated_trade
        self.save_trades()
        
        logger.info(f"Closed {trade.side} trade for {trade.quantity} {trade.symbol} at ${exit_price}, P&L: ${pnl:.2f} ({pnl_percent:.2f}%)")
        return updated_trade
    
    def get_trade(self, trade_id: str) -> Optional[Trade]:
        """Get a trade by ID"""
        return self.trades.get(trade_id)
    
    def get_open_trades(self) -> List[Trade]:
        """Get all open trades"""
        return [t for t in self.trades.values() if t.status == "open"]
    
    def get_closed_trades(self) -> List[Trade]:
        """Get all closed trades"""
        return [t for t in self.trades.values() if t.status == "closed"]
    
    def get_trades_by_symbol(self, symbol: str) -> List[Trade]:
        """Get all trades for a symbol"""
        return [t for t in self.trades.values() if t.symbol == symbol]
    
    def get_trades_by_strategy(self, strategy: str) -> List[Trade]:
        """Get all trades for a strategy"""
        return [t for t in self.trades.values() if t.strategy == strategy]
    
    def get_performance_metrics(self, starting_balance: float = 10000.0) -> PerformanceMetrics:
        """Get performance metrics for all trades"""
        return PerformanceMetrics(list(self.trades.values()), starting_balance)
    
    def update_from_positions(self) -> None:
        """Update open trades from current broker positions"""
        active_broker = self.broker_manager.get_broker()
        positions = active_broker.get_positions()
        
        # Get current market data for all symbols
        symbols = set([p.symbol for p in positions])
        market_data = {}
        
        for symbol in symbols:
            market_data[symbol] = active_broker.get_market_data(symbol)
        
        # Find open trades that match current positions
        open_trades = self.get_open_trades()
        position_map = {p.symbol: p for p in positions}
        
        for trade in open_trades:
            # If we don't have this position anymore, it might have been closed externally
            if trade.symbol not in position_map:
                # Try to get market data to close the trade
                if trade.symbol in market_data:
                    price = market_data[trade.symbol].get("last")
                    if price:
                        self.close_trade(
                            trade_id=trade.id,
                            exit_price=price,
                            notes="Position closed externally - synchronized from broker"
                        )
                continue
            
            position = position_map[trade.symbol]
            
            # Check if quantity changed
            if position.qty != trade.quantity:
                logger.warning(f"Position quantity for {trade.symbol} changed from {trade.quantity} to {position.qty}")
                
                # Calculate proportional exit if position reduced
                if position.qty < trade.quantity:
                    # Calculate how much was closed
                    closed_qty = trade.quantity - position.qty
                    price = market_data[trade.symbol].get("last", position.current_price)
                    
                    # Adjust this trade's quantity
                    self.trades[trade.id] = Trade(
                        id=trade.id,
                        symbol=trade.symbol,
                        entry_date=trade.entry_date,
                        exit_date=None,
                        entry_price=trade.entry_price,
                        exit_price=None,
                        quantity=position.qty,  # Updated quantity
                        side=trade.side,
                        strategy=trade.strategy,
                        pnl=None,
                        pnl_percent=None,
                        fees=trade.fees,
                        status="open",
                        entry_order_id=trade.entry_order_id,
                        exit_order_id=None,
                        stop_loss=trade.stop_loss,
                        take_profit=trade.take_profit,
                        notes=trade.notes + f"\nPosition partially closed: {closed_qty} units at ${price}",
                        tags=trade.tags
                    )
                    
                    # Create a new closed trade for the portion that was exited
                    if trade.side == "long":
                        pnl = (price - trade.entry_price) * closed_qty - (trade.fees * (closed_qty / trade.quantity))
                        pnl_percent = ((price / trade.entry_price) - 1) * 100
                    else:  # short
                        pnl = (trade.entry_price - price) * closed_qty - (trade.fees * (closed_qty / trade.quantity))
                        pnl_percent = ((trade.entry_price / price) - 1) * 100
                    
                    # Create a new trade for the closed portion
                    partial_trade = Trade(
                        id=str(uuid.uuid4()),
                        symbol=trade.symbol,
                        entry_date=trade.entry_date,
                        exit_date=datetime.datetime.now(),
                        entry_price=trade.entry_price,
                        exit_price=price,
                        quantity=closed_qty,
                        side=trade.side,
                        strategy=trade.strategy,
                        pnl=pnl,
                        pnl_percent=pnl_percent,
                        fees=trade.fees * (closed_qty / trade.quantity),
                        status="closed",
                        entry_order_id=trade.entry_order_id,
                        exit_order_id=None,
                        stop_loss=trade.stop_loss,
                        take_profit=trade.take_profit,
                        notes="Partial position closed - synchronized from broker",
                        tags=trade.tags + ["partial_close"]
                    )
                    
                    self.trades[partial_trade.id] = partial_trade
                    
                elif position.qty > trade.quantity:
                    logger.warning(f"Position size increased externally: {trade.symbol}")
                    # Position size increased - we could create a new trade for the additional quantity
        
        self.save_trades() 