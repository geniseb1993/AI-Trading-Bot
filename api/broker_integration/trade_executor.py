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
        limit_price: float,
        time_in_force: str = "day"
    ) -> Optional[Order]:
        """Execute a limit order"""
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        
        tif_map = {
            "day": TimeInForce.DAY,
            "gtc": TimeInForce.GTC,
            "ioc": TimeInForce.IOC,
            "fok": TimeInForce.FOK
        }
        order_tif = tif_map.get(time_in_force.lower(), TimeInForce.DAY)
        
        logger.info(f"Executing limit order: {side} {qty} {symbol} @ ${limit_price}")
        
        try:
            order = self.active_broker.submit_order(
                symbol=symbol,
                qty=qty,
                side=order_side,
                type=OrderType.LIMIT,
                limit_price=limit_price,
                time_in_force=order_tif
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
        stop_price: float,
        time_in_force: str = "day"
    ) -> Optional[Order]:
        """Execute a stop order"""
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        
        tif_map = {
            "day": TimeInForce.DAY,
            "gtc": TimeInForce.GTC,
            "ioc": TimeInForce.IOC,
            "fok": TimeInForce.FOK
        }
        order_tif = tif_map.get(time_in_force.lower(), TimeInForce.DAY)
        
        logger.info(f"Executing stop order: {side} {qty} {symbol} @ ${stop_price}")
        
        try:
            order = self.active_broker.submit_order(
                symbol=symbol,
                qty=qty,
                side=order_side,
                type=OrderType.STOP,
                stop_price=stop_price,
                time_in_force=order_tif
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
        limit_price: float,
        time_in_force: str = "day"
    ) -> Optional[Order]:
        """Execute a stop-limit order"""
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        
        tif_map = {
            "day": TimeInForce.DAY,
            "gtc": TimeInForce.GTC,
            "ioc": TimeInForce.IOC,
            "fok": TimeInForce.FOK
        }
        order_tif = tif_map.get(time_in_force.lower(), TimeInForce.DAY)
        
        logger.info(f"Executing stop-limit order: {side} {qty} {symbol} @ stop ${stop_price}, limit ${limit_price}")
        
        try:
            order = self.active_broker.submit_order(
                symbol=symbol,
                qty=qty,
                side=order_side,
                type=OrderType.STOP_LIMIT,
                stop_price=stop_price,
                limit_price=limit_price,
                time_in_force=order_tif
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
        trail_percent: float,
        time_in_force: str = "day"
    ) -> Optional[Order]:
        """Execute a trailing stop order"""
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        
        tif_map = {
            "day": TimeInForce.DAY,
            "gtc": TimeInForce.GTC,
            "ioc": TimeInForce.IOC,
            "fok": TimeInForce.FOK
        }
        order_tif = tif_map.get(time_in_force.lower(), TimeInForce.DAY)
        
        logger.info(f"Executing trailing stop order: {side} {qty} {symbol} @ {trail_percent}% trail")
        
        try:
            order = self.active_broker.submit_order(
                symbol=symbol,
                qty=qty,
                side=order_side,
                type=OrderType.TRAILING_STOP,
                trail_percent=trail_percent,
                time_in_force=order_tif
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
        logger.info(f"Canceling order: {order_id}")
        
        try:
            result = self.active_broker.cancel_order(order_id)
            if result:
                logger.info(f"Order {order_id} canceled successfully")
            else:
                logger.error(f"Failed to cancel order {order_id}")
            return result
        except Exception as e:
            logger.error(f"Error canceling order: {e}")
            return False
    
    def execute_entry_with_stop_loss(
        self, 
        symbol: str, 
        qty: float, 
        side: str,
        entry_price: Optional[float] = None,  # If None, use market order
        stop_loss_price: float = None,  # Required for risk management
        take_profit_price: Optional[float] = None,  # Optional profit target
        use_market_order: bool = False  # Force market order even if entry_price is provided
    ) -> Dict[str, Any]:
        """
        Execute a complete trade entry with stop loss and optional take profit
        Returns a dictionary with entry and stop/target orders
        """
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        stop_side = OrderSide.SELL if order_side == OrderSide.BUY else OrderSide.BUY
        
        # Validate stop loss is specified
        if stop_loss_price is None:
            logger.error("Stop loss price is required for risk management")
            return {"success": False, "error": "Stop loss price is required"}
        
        # Validate stop loss is in the right direction
        if order_side == OrderSide.BUY and stop_loss_price >= (entry_price or float('inf')):
            logger.error(f"Invalid stop loss price ${stop_loss_price} for long position")
            return {"success": False, "error": "Stop loss must be below entry price for long positions"}
        
        if order_side == OrderSide.SELL and stop_loss_price <= (entry_price or 0):
            logger.error(f"Invalid stop loss price ${stop_loss_price} for short position")
            return {"success": False, "error": "Stop loss must be above entry price for short positions"}
        
        # Execute entry order
        entry_order = None
        if use_market_order or entry_price is None:
            entry_order = self.market_order(symbol, qty, side)
        else:
            entry_order = self.limit_order(symbol, qty, side, entry_price)
        
        if not entry_order:
            return {"success": False, "error": "Failed to place entry order"}
        
        result = {
            "success": True,
            "entry_order": entry_order.to_dict(),
            "stop_loss_order": None,
            "take_profit_order": None
        }
        
        # For market orders, wait for fill then place stop loss
        if entry_order.type == OrderType.MARKET:
            # Should already be filled, but just in case
            # In a real system you would want to poll for the order status
            time.sleep(1)
            
            # Place stop loss order
            stop_loss_order = self.stop_order(
                symbol=symbol,
                qty=qty,
                side="sell" if order_side == OrderSide.BUY else "buy",
                stop_price=stop_loss_price,
                time_in_force="gtc"
            )
            
            if stop_loss_order:
                result["stop_loss_order"] = stop_loss_order.to_dict()
            
            # Place take profit order if specified
            if take_profit_price:
                take_profit_order = self.limit_order(
                    symbol=symbol,
                    qty=qty,
                    side="sell" if order_side == OrderSide.BUY else "buy",
                    limit_price=take_profit_price,
                    time_in_force="gtc"
                )
                
                if take_profit_order:
                    result["take_profit_order"] = take_profit_order.to_dict()
        
        # For limit orders, we would need to monitor for fill before placing stop loss
        # In a real system, you would use broker's API callback or poll for order status
        
        return result
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get the current status of an order"""
        try:
            order = self.active_broker.get_order(order_id)
            if order:
                return {
                    "success": True,
                    "order": order.to_dict()
                }
            else:
                return {
                    "success": False,
                    "error": f"Order {order_id} not found"
                }
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
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