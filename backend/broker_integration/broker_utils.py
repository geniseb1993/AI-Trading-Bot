"""
Broker Utilities Module

This module provides utility functions for working with brokers.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

from .broker_interface import OrderStatus, OrderSide, OrderType, TimeInForce
from .config import load_config, save_config, get_active_broker_config

logger = logging.getLogger(__name__)

def format_order_for_response(order: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format an order for API response.
    
    Args:
        order: Order dictionary from broker
        
    Returns:
        Formatted order dictionary
    """
    # Create a new dict with selected fields
    formatted = {
        "id": order.get("id"),
        "symbol": order.get("symbol"),
        "qty": order.get("qty"),
        "side": order.get("side"),
        "type": order.get("type"),
        "status": order.get("status"),
        "created_at": order.get("created_at"),
        "filled_at": order.get("filled_at"),
        "filled_qty": order.get("filled_qty", 0),
        "filled_avg_price": order.get("filled_avg_price")
    }
    
    # Add optional fields if present
    if "limit_price" in order:
        formatted["limit_price"] = order["limit_price"]
    
    if "stop_price" in order:
        formatted["stop_price"] = order["stop_price"]
    
    # Add calculated fields
    formatted["is_filled"] = order.get("status") == "filled"
    formatted["is_active"] = order.get("status") in ["new", "partially_filled", "held"]
    
    # Format timestamps
    if isinstance(formatted.get("created_at"), datetime):
        formatted["created_at"] = formatted["created_at"].isoformat()
    
    if isinstance(formatted.get("filled_at"), datetime):
        formatted["filled_at"] = formatted["filled_at"].isoformat()
    
    return formatted

def format_position_for_response(position: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a position for API response.
    
    Args:
        position: Position dictionary from broker
        
    Returns:
        Formatted position dictionary
    """
    # Create a new dict with selected fields
    formatted = {
        "symbol": position.get("symbol"),
        "qty": position.get("qty"),
        "avg_entry_price": position.get("avg_entry_price"),
        "current_price": position.get("current_price"),
        "market_value": position.get("market_value"),
        "unrealized_pl": position.get("unrealized_pl"),
        "unrealized_pl_percent": position.get("unrealized_pl_percent")
    }
    
    # Add side if present
    if "side" in position:
        formatted["side"] = position["side"]
    
    return formatted

def format_account_for_response(account: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format an account for API response.
    
    Args:
        account: Account dictionary from broker
        
    Returns:
        Formatted account dictionary
    """
    # Create a new dict with selected fields
    formatted = {
        "id": account.get("id"),
        "cash": account.get("cash"),
        "portfolio_value": account.get("portfolio_value"),
        "buying_power": account.get("buying_power"),
        "equity": account.get("equity"),
        "currency": account.get("currency", "USD")
    }
    
    return formatted

def get_order_history(data_dir: str = "api/broker_integration/data") -> List[Dict[str, Any]]:
    """
    Get order history from the data directory.
    
    Args:
        data_dir: Directory where order history is stored
        
    Returns:
        List of order dictionaries
    """
    orders_file = os.path.join(data_dir, "order_history.json")
    
    if not os.path.exists(orders_file):
        return []
    
    try:
        with open(orders_file, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading order history: {e}")
        return []

def save_order_history(orders: List[Dict[str, Any]], data_dir: str = "api/broker_integration/data") -> bool:
    """
    Save order history to the data directory.
    
    Args:
        orders: List of order dictionaries
        data_dir: Directory where order history is stored
        
    Returns:
        True if successful, False otherwise
    """
    os.makedirs(data_dir, exist_ok=True)
    orders_file = os.path.join(data_dir, "order_history.json")
    
    try:
        with open(orders_file, "w") as f:
            json.dump(orders, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving order history: {e}")
        return False

def calculate_order_notional(order: Dict[str, Any]) -> float:
    """
    Calculate the notional value of an order.
    
    Args:
        order: Order dictionary
        
    Returns:
        Notional value of the order
    """
    # If order is filled or partially filled, use filled data
    if order.get("filled_qty") and order.get("filled_avg_price"):
        return float(order["filled_qty"]) * float(order["filled_avg_price"])
    
    # For limit orders, use limit price
    if order.get("type") == "limit" and order.get("limit_price"):
        return float(order["qty"]) * float(order["limit_price"])
    
    # For market orders or other cases, return 0 (can't calculate exactly)
    return 0.0

def get_trade_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    data_dir: str = "api/broker_integration/data"
) -> Dict[str, Any]:
    """
    Calculate trading statistics.
    
    Args:
        start_date: Start date for statistics
        end_date: End date for statistics
        data_dir: Directory where order history is stored
        
    Returns:
        Dictionary with trading statistics
    """
    # Default date range if not provided
    if not end_date:
        end_date = datetime.now()
    
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get order history
    orders = get_order_history(data_dir)
    
    # Filter orders by date
    filtered_orders = []
    for order in orders:
        if "filled_at" in order and order.get("filled_at"):
            # Convert string to datetime if needed
            if isinstance(order["filled_at"], str):
                filled_at = datetime.fromisoformat(order["filled_at"].replace("Z", "+00:00"))
            else:
                filled_at = order["filled_at"]
            
            if start_date <= filled_at <= end_date:
                filtered_orders.append(order)
    
    # Calculate statistics
    total_trades = len(filtered_orders)
    winning_trades = 0
    losing_trades = 0
    total_profit = 0.0
    total_loss = 0.0
    
    for order in filtered_orders:
        pl = order.get("realized_pl", 0)
        if pl > 0:
            winning_trades += 1
            total_profit += pl
        elif pl < 0:
            losing_trades += 1
            total_loss += abs(pl)
    
    # Avoid division by zero
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    avg_profit = total_profit / winning_trades if winning_trades > 0 else 0
    avg_loss = total_loss / losing_trades if losing_trades > 0 else 0
    profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
    
    return {
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": win_rate,
        "total_profit": total_profit,
        "total_loss": total_loss,
        "net_profit": total_profit - total_loss,
        "avg_profit": avg_profit,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor
    }

def check_broker_credentials(broker_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if broker credentials are valid.
    
    Args:
        broker_type: Type of broker
        config: Broker configuration
        
    Returns:
        Dictionary with validation results
    """
    result = {
        "is_valid": False,
        "missing_fields": [],
        "error": None
    }
    
    if broker_type == "alpaca":
        # Check required fields
        required_fields = ["api_key", "api_secret"]
        for field in required_fields:
            if not config.get(field):
                result["missing_fields"].append(field)
        
        if result["missing_fields"]:
            result["error"] = f"Missing required fields: {', '.join(result['missing_fields'])}"
            return result
        
        # Fields are present, but we can't verify them without making an API call
        # This would typically be done in the AlpacaBroker class
        result["is_valid"] = True
    
    elif broker_type == "mock":
        # Mock broker doesn't need credentials
        result["is_valid"] = True
    
    else:
        result["error"] = f"Unsupported broker type: {broker_type}"
    
    return result

def set_broker_credentials(broker_type: str, credentials: Dict[str, Any], config_path: Optional[str] = None) -> bool:
    """
    Set credentials for a broker.
    
    Args:
        broker_type: Type of broker
        credentials: Dictionary with credentials
        config_path: Path to the broker configuration file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Load current config
        config = load_config(config_path)
        
        # Ensure broker entry exists
        if "brokers" not in config:
            config["brokers"] = {}
        
        if broker_type not in config["brokers"]:
            config["brokers"][broker_type] = {}
        
        # Update credentials
        for key, value in credentials.items():
            config["brokers"][broker_type][key] = value
        
        # Save config
        return save_config(config, config_path or "broker_config.json")
    
    except Exception as e:
        logger.error(f"Error setting broker credentials: {e}")
        return False 