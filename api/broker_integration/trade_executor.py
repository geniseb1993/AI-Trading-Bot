import logging
import time
import datetime
from typing import Dict, List, Optional, Any, Union, Tuple

from .broker_interface import (
    BrokerInterface,
    Order,
    OrderSide,
    OrderType,
    OrderStatus,
    TimeInForce
)
from .broker_manager import BrokerManager

logger = logging.getLogger(__name__)

class TradeExecutor:
    """Handles execution of trade strategies and execution algorithms"""
    
    def __init__(self, broker_manager: BrokerManager):
        """Initialize with a broker manager"""
        self.broker_manager = broker_manager
        self.active_broker = broker_manager.get_broker()
    
    def set_broker(self, broker_name: Optional[str] = None):
        """Set the active broker for trade execution"""
        self.active_broker = self.broker_manager.get_broker(broker_name)
        return self.active_broker.__class__.__name__
    
    def market_order(
        self, 
        symbol: str, 
        qty: float, 
        side: str
    ) -> Optional[Order]:
        """Execute a simple market order"""
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        
        logger.info(f"Executing market order: {side} {qty} {symbol}")
        
        try:
            order = self.active_broker.submit_order(
                symbol=symbol,
                qty=qty,
                side=order_side,
                type=OrderType.MARKET,
                time_in_force=TimeInForce.DAY
            )
            
            if order:
                logger.info(f"Market order executed: {order.id}")
                return order
            else:
                logger.error(f"Failed to execute market order for {symbol}")
                return None
        except Exception as e:
            logger.error(f"Error executing market order: {e}")
            return None
    
    def limit_order(
        self, 
        symbol: str, 
        qty: float, 
        side: str, 
        limit_price: float
    ) -> Optional[Order]:
        """Execute a limit order"""
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        
        logger.info(f"Executing limit order: {side} {qty} {symbol} @ ${limit_price}")
        
        try:
            order = self.active_broker.submit_order(
                symbol=symbol,
                qty=qty,
                side=order_side,
                type=OrderType.LIMIT,
                limit_price=limit_price,
                time_in_force=TimeInForce.DAY
            )
            
            if order:
                logger.info(f"Limit order placed: {order.id}")
                return order
            else:
                logger.error(f"Failed to place limit order for {symbol}")
                return None
        except Exception as e:
            logger.error(f"Error placing limit order: {e}")
            return None
    
    def stop_order(
        self, 
        symbol: str, 
        qty: float, 
        side: str, 
        stop_price: float
    ) -> Optional[Order]:
        """Execute a stop order"""
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        
        logger.info(f"Executing stop order: {side} {qty} {symbol} @ ${stop_price}")
        
        try:
            order = self.active_broker.submit_order(
                symbol=symbol,
                qty=qty,
                side=order_side,
                type=OrderType.STOP,
                stop_price=stop_price,
                time_in_force=TimeInForce.DAY
            )
            
            if order:
                logger.info(f"Stop order placed: {order.id}")
                return order
            else:
                logger.error(f"Failed to place stop order for {symbol}")
                return None
        except Exception as e:
            logger.error(f"Error placing stop order: {e}")
            return None
    
    def stop_limit_order(
        self, 
        symbol: str, 
        qty: float, 
        side: str, 
        stop_price: float,
        limit_price: float
    ) -> Optional[Order]:
        """Execute a stop-limit order"""
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        
        logger.info(f"Executing stop-limit order: {side} {qty} {symbol} @ stop ${stop_price}, limit ${limit_price}")
        
        try:
            order = self.active_broker.submit_order(
                symbol=symbol,
                qty=qty,
                side=order_side,
                type=OrderType.STOP_LIMIT,
                stop_price=stop_price,
                limit_price=limit_price,
                time_in_force=TimeInForce.DAY
            )
            
            if order:
                logger.info(f"Stop-limit order placed: {order.id}")
                return order
            else:
                logger.error(f"Failed to place stop-limit order for {symbol}")
                return None
        except Exception as e:
            logger.error(f"Error placing stop-limit order: {e}")
            return None
    
    def trailing_stop_order(
        self, 
        symbol: str, 
        qty: float, 
        side: str, 
        trail_percent: float
    ) -> Optional[Order]:
        """Execute a trailing stop order"""
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        
        logger.info(f"Executing trailing stop order: {side} {qty} {symbol} @ {trail_percent}% trail")
        
        try:
            order = self.active_broker.submit_order(
                symbol=symbol,
                qty=qty,
                side=order_side,
                type=OrderType.TRAILING_STOP,
                trail_percent=trail_percent,
                time_in_force=TimeInForce.DAY
            )
            
            if order:
                logger.info(f"Trailing stop order placed: {order.id}")
                return order
            else:
                logger.error(f"Failed to place trailing stop order for {symbol}")
                return None
        except Exception as e:
            logger.error(f"Error placing trailing stop order: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order"""
        try:
            result = self.active_broker.cancel_order(order_id)
            if result:
                logger.info(f"Order cancelled: {order_id}")
            else:
                logger.error(f"Failed to cancel order: {order_id}")
            return result
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    def cancel_all_orders(self) -> bool:
        """Cancel all open orders"""
        try:
            result = self.active_broker.cancel_all_orders()
            if result:
                logger.info("All orders cancelled")
            else:
                logger.error("Failed to cancel all orders")
            return result
        except Exception as e:
            logger.error(f"Error cancelling all orders: {e}")
            return False
    
    def get_open_orders(self) -> List[Order]:
        """Get all open orders"""
        try:
            return self.active_broker.get_orders(status=OrderStatus.NEW)
        except Exception as e:
            logger.error(f"Error getting open orders: {e}")
            return []
    
    def get_order_status(self, order_id: str) -> Optional[OrderStatus]:
        """Get the status of a specific order"""
        try:
            order = self.active_broker.get_order(order_id)
            if order:
                return order.status
            return None
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            return None
    
    def place_bracket_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        entry_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
        stop_loss_price: Optional[float] = None,
        take_profit_percent: Optional[float] = None,
        stop_loss_percent: Optional[float] = None
    ) -> Tuple[Optional[Order], Optional[Order], Optional[Order]]:
        """
        Place a bracket order (entry order + take profit + stop loss)
        
        Args:
            symbol: The symbol to trade
            qty: The quantity to trade
            side: Buy or sell
            entry_price: Limit price for entry (None for market order)
            take_profit_price: Price for take profit order
            stop_loss_price: Price for stop loss order
            take_profit_percent: Alternative to take_profit_price (% from entry)
            stop_loss_percent: Alternative to stop_loss_price (% from entry)
            
        Returns:
            Tuple of (entry_order, take_profit_order, stop_loss_order)
        """
        # Validate arguments
        if take_profit_price is None and take_profit_percent is None:
            logger.error("Either take_profit_price or take_profit_percent must be provided")
            return None, None, None
            
        if stop_loss_price is None and stop_loss_percent is None:
            logger.error("Either stop_loss_price or stop_loss_percent must be provided")
            return None, None, None
        
        # Determine if we're using market or limit entry
        is_market_entry = entry_price is None
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        
        # For market orders, we need to estimate the entry price
        if is_market_entry:
            # Get current market data
            market_data = self.active_broker.get_market_data(symbol)
            if order_side == OrderSide.BUY:
                estimated_entry = market_data.get("ask", market_data.get("last"))
            else:
                estimated_entry = market_data.get("bid", market_data.get("last"))
            
            # Calculate take profit and stop loss if using percentages
            if take_profit_percent is not None:
                if order_side == OrderSide.BUY:
                    take_profit_price = estimated_entry * (1 + take_profit_percent / 100)
                else:
                    take_profit_price = estimated_entry * (1 - take_profit_percent / 100)
            
            if stop_loss_percent is not None:
                if order_side == OrderSide.BUY:
                    stop_loss_price = estimated_entry * (1 - stop_loss_percent / 100)
                else:
                    stop_loss_price = estimated_entry * (1 + stop_loss_percent / 100)
            
            # Place market entry order
            entry_order = self.market_order(symbol, qty, side)
            
        else:
            # Calculate take profit and stop loss if using percentages
            if take_profit_percent is not None:
                if order_side == OrderSide.BUY:
                    take_profit_price = entry_price * (1 + take_profit_percent / 100)
                else:
                    take_profit_price = entry_price * (1 - take_profit_percent / 100)
            
            if stop_loss_percent is not None:
                if order_side == OrderSide.BUY:
                    stop_loss_price = entry_price * (1 - stop_loss_percent / 100)
                else:
                    stop_loss_price = entry_price * (1 + stop_loss_percent / 100)
            
            # Place limit entry order
            entry_order = self.limit_order(symbol, qty, side, entry_price)
        
        if not entry_order:
            logger.error("Failed to place entry order")
            return None, None, None
        
        # Set up opposite side for exit orders
        exit_side = "sell" if order_side == OrderSide.BUY else "buy"
        
        # Place take profit order
        take_profit_order = self.limit_order(
            symbol=symbol,
            qty=qty,
            side=exit_side,
            limit_price=take_profit_price
        )
        
        # Place stop loss order
        stop_loss_order = self.stop_order(
            symbol=symbol,
            qty=qty,
            side=exit_side,
            stop_price=stop_loss_price
        )
        
        logger.info(f"Placed bracket order for {symbol}: Entry={entry_order.id}, TP={take_profit_order.id if take_profit_order else None}, SL={stop_loss_order.id if stop_loss_order else None}")
        
        return entry_order, take_profit_order, stop_loss_order
    
    def get_positions(self) -> Dict[str, Any]:
        """Get all current positions"""
        try:
            positions = self.active_broker.get_positions()
            return {
                "success": True,
                "positions": [
                    {
                        "symbol": pos.symbol,
                        "qty": pos.qty,
                        "avg_entry_price": pos.avg_entry_price,
                        "current_price": pos.current_price,
                        "side": pos.side,
                        "market_value": pos.market_value,
                        "unrealized_pl": pos.unrealized_pl,
                        "unrealized_pl_pct": pos.unrealized_pl_pct
                    }
                    for pos in positions
                ]
            }
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            account = self.active_broker.get_account()
            return {
                "success": True,
                "account": account.to_dict()
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return {
                "success": False,
                "error": str(e)
            } 