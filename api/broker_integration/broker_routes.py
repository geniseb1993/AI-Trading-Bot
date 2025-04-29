import logging
import datetime
import os
import uuid
from flask import Blueprint, jsonify, request
from typing import Dict, Any

from .broker_manager import BrokerManager
from .trade_executor import TradeExecutor
from .portfolio_tracker import Trade, PortfolioTracker

logger = logging.getLogger(__name__)

# Create a Flask Blueprint
broker_bp = Blueprint('broker', __name__, url_prefix='/api/broker')

# Create instances
broker_manager = BrokerManager(config_file=os.path.join(os.path.dirname(__file__), "broker_config.json"))
trade_executor = TradeExecutor(broker_manager)
portfolio_tracker = PortfolioTracker(broker_manager, trades_file=os.path.join(os.path.dirname(__file__), "trade_history.json"))

# Routes

@broker_bp.route('/info', methods=['GET'])
def get_broker_info():
    """Get information about available brokers"""
    try:
        available_brokers = broker_manager.get_available_brokers()
        active_broker = broker_manager.active_broker_name
        
        return jsonify({
            'success': True,
            'available_brokers': available_brokers,
            'active_broker': active_broker
        })
    except Exception as e:
        logger.error(f"Error getting broker info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/set-active', methods=['POST'])
def set_active_broker():
    """Set the active broker"""
    try:
        data = request.json
        broker_name = data.get('broker_name')
        
        if not broker_name:
            return jsonify({
                'success': False,
                'error': 'Broker name is required'
            }), 400
        
        result = broker_manager.set_active_broker(broker_name)
        
        if result:
            # Update trade executor to use the new broker
            trade_executor.set_broker(broker_name)
            
            return jsonify({
                'success': True,
                'active_broker': broker_name
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to set {broker_name} as active broker'
            }), 400
    except Exception as e:
        logger.error(f"Error setting active broker: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/configure', methods=['POST'])
def configure_broker():
    """Configure a broker"""
    try:
        data = request.json
        broker_name = data.get('broker_name')
        config = data.get('config', {})
        
        if not broker_name:
            return jsonify({
                'success': False,
                'error': 'Broker name is required'
            }), 400
        
        result = broker_manager.update_broker_config(broker_name, config)
        
        return jsonify({
            'success': result,
            'message': f'Broker {broker_name} configuration updated' if result else f'Failed to update broker configuration'
        })
    except Exception as e:
        logger.error(f"Error configuring broker: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/account', methods=['GET'])
def get_account_info():
    """Get account information from active broker"""
    try:
        broker = broker_manager.get_broker()
        account = broker.get_account()
        
        return jsonify({
            'success': True,
            'account': account.to_dict()
        })
    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/positions', methods=['GET'])
def get_positions():
    """Get current positions from active broker"""
    try:
        broker = broker_manager.get_broker()
        positions = broker.get_positions()
        
        return jsonify({
            'success': True,
            'positions': [
                {
                    'symbol': p.symbol,
                    'qty': p.qty,
                    'avg_entry_price': p.avg_entry_price,
                    'current_price': p.current_price,
                    'market_value': p.market_value,
                    'unrealized_pl': p.unrealized_pl,
                    'unrealized_pl_pct': p.unrealized_pl_pct
                }
                for p in positions
            ]
        })
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/orders', methods=['GET'])
def get_orders():
    """Get orders from active broker"""
    try:
        broker = broker_manager.get_broker()
        status = request.args.get('status')
        
        # Convert status string to enum if provided
        order_status = None
        if status:
            from .broker_interface import OrderStatus
            status_map = {
                'new': OrderStatus.NEW,
                'filled': OrderStatus.FILLED,
                'partially_filled': OrderStatus.PARTIALLY_FILLED,
                'cancelled': OrderStatus.CANCELLED,
                'rejected': OrderStatus.REJECTED,
                'expired': OrderStatus.EXPIRED
            }
            order_status = status_map.get(status.lower())
        
        orders = broker.get_orders(status=order_status)
        
        return jsonify({
            'success': True,
            'orders': [order.to_dict() for order in orders]
        })
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/market-data', methods=['GET'])
def get_market_data():
    """Get market data for a symbol"""
    try:
        symbol = request.args.get('symbol')
        
        if not symbol:
            return jsonify({
                'success': False,
                'error': 'Symbol is required'
            }), 400
        
        broker = broker_manager.get_broker()
        market_data = broker.get_market_data(symbol)
        
        return jsonify({
            'success': True,
            'market_data': market_data
        })
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/execute/market', methods=['POST'])
def execute_market_order():
    """Execute a market order"""
    try:
        data = request.json
        symbol = data.get('symbol')
        qty = data.get('qty')
        side = data.get('side')
        
        # Validate required fields
        if not symbol or not qty or not side:
            return jsonify({
                'success': False,
                'error': 'Symbol, qty, and side are required'
            }), 400
        
        # Convert qty to float
        try:
            qty = float(qty)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Qty must be a number'
            }), 400
        
        # Validate side
        if side.lower() not in ['buy', 'sell']:
            return jsonify({
                'success': False,
                'error': 'Side must be buy or sell'
            }), 400
        
        # Execute order
        order = trade_executor.market_order(symbol, qty, side)
        
        if order:
            # Create a trade record
            trade = portfolio_tracker.open_trade(
                symbol=symbol,
                quantity=qty,
                entry_price=order.filled_avg_price or 0.0,
                side='long' if side.lower() == 'buy' else 'short',
                strategy=data.get('strategy', 'manual'),
                entry_order_id=order.id,
                stop_loss=data.get('stop_loss'),
                take_profit=data.get('take_profit'),
                notes=data.get('notes'),
                tags=data.get('tags', [])
            )
            
            return jsonify({
                'success': True,
                'order': order.to_dict(),
                'trade_id': trade.id
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to execute market order'
            }), 400
    except Exception as e:
        logger.error(f"Error executing market order: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/execute/limit', methods=['POST'])
def execute_limit_order():
    """Execute a limit order"""
    try:
        data = request.json
        symbol = data.get('symbol')
        qty = data.get('qty')
        side = data.get('side')
        limit_price = data.get('limit_price')
        
        # Validate required fields
        if not symbol or not qty or not side or not limit_price:
            return jsonify({
                'success': False,
                'error': 'Symbol, qty, side, and limit_price are required'
            }), 400
        
        # Convert numeric values
        try:
            qty = float(qty)
            limit_price = float(limit_price)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Qty and limit_price must be numbers'
            }), 400
        
        # Validate side
        if side.lower() not in ['buy', 'sell']:
            return jsonify({
                'success': False,
                'error': 'Side must be buy or sell'
            }), 400
        
        # Execute order
        order = trade_executor.limit_order(symbol, qty, side, limit_price)
        
        if order:
            # Create a trade record
            trade = portfolio_tracker.open_trade(
                symbol=symbol,
                quantity=qty,
                entry_price=limit_price,  # This is just an estimate until the order fills
                side='long' if side.lower() == 'buy' else 'short',
                strategy=data.get('strategy', 'manual'),
                entry_order_id=order.id,
                stop_loss=data.get('stop_loss'),
                take_profit=data.get('take_profit'),
                notes=data.get('notes'),
                tags=data.get('tags', [])
            )
            
            return jsonify({
                'success': True,
                'order': order.to_dict(),
                'trade_id': trade.id
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to execute limit order'
            }), 400
    except Exception as e:
        logger.error(f"Error executing limit order: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/execute/bracket', methods=['POST'])
def execute_bracket_order():
    """Execute a bracket order (entry + take profit + stop loss)"""
    try:
        data = request.json
        symbol = data.get('symbol')
        qty = data.get('qty')
        side = data.get('side')
        entry_price = data.get('entry_price')  # Optional for market orders
        take_profit_price = data.get('take_profit_price')
        stop_loss_price = data.get('stop_loss_price')
        take_profit_percent = data.get('take_profit_percent')
        stop_loss_percent = data.get('stop_loss_percent')
        
        # Validate required fields
        if not symbol or not qty or not side:
            return jsonify({
                'success': False,
                'error': 'Symbol, qty, and side are required'
            }), 400
        
        # Convert numeric values
        try:
            qty = float(qty)
            if entry_price:
                entry_price = float(entry_price)
            if take_profit_price:
                take_profit_price = float(take_profit_price)
            if stop_loss_price:
                stop_loss_price = float(stop_loss_price)
            if take_profit_percent:
                take_profit_percent = float(take_profit_percent)
            if stop_loss_percent:
                stop_loss_percent = float(stop_loss_percent)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid numeric value'
            }), 400
        
        # Validate side
        if side.lower() not in ['buy', 'sell']:
            return jsonify({
                'success': False,
                'error': 'Side must be buy or sell'
            }), 400
        
        # Execute bracket order
        entry_order, take_profit_order, stop_loss_order = trade_executor.place_bracket_order(
            symbol=symbol,
            qty=qty,
            side=side,
            entry_price=entry_price,
            take_profit_price=take_profit_price,
            stop_loss_price=stop_loss_price,
            take_profit_percent=take_profit_percent,
            stop_loss_percent=stop_loss_percent
        )
        
        if entry_order:
            # Get the price from the order or entry_price
            price = entry_order.filled_avg_price or entry_price or 0.0
            
            # Create a trade record
            trade = portfolio_tracker.open_trade(
                symbol=symbol,
                quantity=qty,
                entry_price=price,
                side='long' if side.lower() == 'buy' else 'short',
                strategy=data.get('strategy', 'manual'),
                entry_order_id=entry_order.id,
                stop_loss=stop_loss_price,
                take_profit=take_profit_price,
                notes=data.get('notes'),
                tags=data.get('tags', [])
            )
            
            return jsonify({
                'success': True,
                'entry_order': entry_order.to_dict(),
                'take_profit_order': take_profit_order.to_dict() if take_profit_order else None,
                'stop_loss_order': stop_loss_order.to_dict() if stop_loss_order else None,
                'trade_id': trade.id
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to execute bracket order'
            }), 400
    except Exception as e:
        logger.error(f"Error executing bracket order: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/cancel-order/<order_id>', methods=['DELETE'])
def cancel_order(order_id):
    """Cancel an order"""
    try:
        result = trade_executor.cancel_order(order_id)
        
        return jsonify({
            'success': result,
            'message': f'Order {order_id} cancelled' if result else f'Failed to cancel order {order_id}'
        })
    except Exception as e:
        logger.error(f"Error cancelling order: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/cancel-all-orders', methods=['DELETE'])
def cancel_all_orders():
    """Cancel all open orders"""
    try:
        result = trade_executor.cancel_all_orders()
        
        return jsonify({
            'success': result,
            'message': 'All orders cancelled' if result else 'Failed to cancel all orders'
        })
    except Exception as e:
        logger.error(f"Error cancelling all orders: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Portfolio tracking routes

@broker_bp.route('/trades', methods=['GET'])
def get_trades():
    """Get all trades with optional filtering"""
    try:
        status = request.args.get('status')
        symbol = request.args.get('symbol')
        strategy = request.args.get('strategy')
        
        trades = []
        
        # Filter by status
        if status == 'open':
            trades = portfolio_tracker.get_open_trades()
        elif status == 'closed':
            trades = portfolio_tracker.get_closed_trades()
        else:
            # Get all trades
            trades = list(portfolio_tracker.trades.values())
        
        # Filter by symbol
        if symbol:
            trades = [t for t in trades if t.symbol == symbol]
        
        # Filter by strategy
        if strategy:
            trades = [t for t in trades if t.strategy == strategy]
        
        return jsonify({
            'success': True,
            'trades': [t.to_dict() for t in trades]
        })
    except Exception as e:
        logger.error(f"Error getting trades: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/trades/<trade_id>', methods=['GET'])
def get_trade(trade_id):
    """Get a specific trade by ID"""
    try:
        trade = portfolio_tracker.get_trade(trade_id)
        
        if trade:
            return jsonify({
                'success': True,
                'trade': trade.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Trade {trade_id} not found'
            }), 404
    except Exception as e:
        logger.error(f"Error getting trade: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/trades/<trade_id>/close', methods=['POST'])
def close_trade(trade_id):
    """Close a trade"""
    try:
        data = request.json
        exit_price = data.get('exit_price')
        exit_order_id = data.get('exit_order_id')
        fees = data.get('fees')
        notes = data.get('notes')
        
        # Validate required fields
        if not exit_price:
            return jsonify({
                'success': False,
                'error': 'Exit price is required'
            }), 400
        
        # Convert numeric values
        try:
            exit_price = float(exit_price)
            if fees:
                fees = float(fees)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid numeric value'
            }), 400
        
        # Close the trade
        trade = portfolio_tracker.close_trade(
            trade_id=trade_id,
            exit_price=exit_price,
            exit_order_id=exit_order_id,
            fees=fees,
            notes=notes
        )
        
        if trade:
            return jsonify({
                'success': True,
                'trade': trade.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to close trade {trade_id}'
            }), 400
    except Exception as e:
        logger.error(f"Error closing trade: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/performance', methods=['GET'])
def get_performance():
    """Get performance metrics"""
    try:
        starting_balance = request.args.get('starting_balance')
        
        # Convert starting balance if provided
        if starting_balance:
            try:
                starting_balance = float(starting_balance)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Starting balance must be a number'
                }), 400
        else:
            starting_balance = 10000.0  # Default
        
        metrics = portfolio_tracker.get_performance_metrics(starting_balance)
        
        return jsonify({
            'success': True,
            'metrics': metrics.to_dict()
        })
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/sync', methods=['POST'])
def sync_portfolio():
    """Synchronize portfolio with current broker positions"""
    try:
        portfolio_tracker.update_from_positions()
        
        return jsonify({
            'success': True,
            'message': 'Portfolio synchronized with broker positions'
        })
    except Exception as e:
        logger.error(f"Error synchronizing portfolio: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def register_routes(app):
    """Register broker routes with Flask app"""
    app.register_blueprint(broker_bp)
    logger.info("Registered broker routes") 