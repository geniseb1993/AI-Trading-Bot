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
    """Get account information"""
    try:
        account_info = trade_executor.get_account_info()
        return jsonify(account_info)
    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/positions', methods=['GET'])
def get_positions():
    """Get current positions"""
    try:
        positions = trade_executor.get_positions()
        return jsonify(positions)
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
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

@broker_bp.route('/order', methods=['POST'])
def place_order():
    """Place a new order"""
    try:
        data = request.json
        order_type = data.get('type', 'market').lower()
        
        # Required for all order types
        symbol = data.get('symbol')
        side = data.get('side')
        qty = data.get('qty')
        
        if not all([symbol, side, qty]):
            return jsonify({
                'success': False,
                'error': 'Symbol, side, and quantity are required'
            }), 400
        
        # Execute the order based on type
        if order_type == 'market':
            order = trade_executor.market_order(symbol, float(qty), side)
        elif order_type == 'limit':
            limit_price = data.get('limit_price')
            time_in_force = data.get('time_in_force', 'day')
            
            if not limit_price:
                return jsonify({
                    'success': False,
                    'error': 'Limit price is required for limit orders'
                }), 400
            
            order = trade_executor.limit_order(symbol, float(qty), side, float(limit_price), time_in_force)
        elif order_type == 'stop':
            stop_price = data.get('stop_price')
            time_in_force = data.get('time_in_force', 'day')
            
            if not stop_price:
                return jsonify({
                    'success': False,
                    'error': 'Stop price is required for stop orders'
                }), 400
            
            order = trade_executor.stop_order(symbol, float(qty), side, float(stop_price), time_in_force)
        elif order_type == 'stop_limit':
            stop_price = data.get('stop_price')
            limit_price = data.get('limit_price')
            time_in_force = data.get('time_in_force', 'day')
            
            if not stop_price or not limit_price:
                return jsonify({
                    'success': False,
                    'error': 'Stop price and limit price are required for stop-limit orders'
                }), 400
            
            order = trade_executor.stop_limit_order(symbol, float(qty), side, float(stop_price), float(limit_price), time_in_force)
        elif order_type == 'trailing_stop':
            trail_percent = data.get('trail_percent')
            time_in_force = data.get('time_in_force', 'day')
            
            if not trail_percent:
                return jsonify({
                    'success': False,
                    'error': 'Trail percent is required for trailing stop orders'
                }), 400
            
            order = trade_executor.trailing_stop_order(symbol, float(qty), side, float(trail_percent), time_in_force)
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported order type: {order_type}'
            }), 400
        
        # Check if order was successful
        if order:
            # Add to portfolio tracker with default stop loss/take profit if provided
            stop_loss_price = data.get('stop_loss_price')
            take_profit_price = data.get('take_profit_price')
            strategy = data.get('strategy', 'default')
            tags = data.get('tags', [])
            notes = data.get('notes', '')
            
            if order.status == 'filled':
                trade = Trade(
                    trade_id=str(uuid.uuid4()),
                    symbol=symbol,
                    side=side,
                    entry_date=datetime.datetime.now(),
                    entry_price=order.filled_avg_price if order.filled_avg_price else order.limit_price or 0.0,
                    entry_order_id=order.id,
                    qty=qty,
                    stop_loss_price=stop_loss_price,
                    take_profit_price=take_profit_price,
                    strategy=strategy,
                    tags=tags,
                    notes=notes
                )
                portfolio_tracker.add_trade(trade)
            
            return jsonify({
                'success': True,
                'order': order.to_dict(),
                'message': 'Order placed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to place order'
            }), 400
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/order/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get order status"""
    try:
        order_status = trade_executor.get_order_status(order_id)
        return jsonify(order_status)
    except Exception as e:
        logger.error(f"Error getting order status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/order/<order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """Cancel an order"""
    try:
        result = trade_executor.cancel_order(order_id)
        
        return jsonify({
            'success': result,
            'message': 'Order canceled successfully' if result else 'Failed to cancel order'
        })
    except Exception as e:
        logger.error(f"Error canceling order: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/entry-with-stop', methods=['POST'])
def entry_with_stop():
    """Place an entry order with stop loss and optional take profit"""
    try:
        data = request.json
        
        # Required parameters
        symbol = data.get('symbol')
        side = data.get('side')
        qty = data.get('qty')
        stop_loss_price = data.get('stop_loss_price')
        
        # Optional parameters
        entry_price = data.get('entry_price')
        take_profit_price = data.get('take_profit_price')
        use_market_order = data.get('use_market_order', False)
        strategy = data.get('strategy', 'default')
        tags = data.get('tags', [])
        notes = data.get('notes', '')
        
        if not all([symbol, side, qty, stop_loss_price]):
            return jsonify({
                'success': False,
                'error': 'Symbol, side, quantity, and stop loss price are required'
            }), 400
        
        # Execute the trade
        result = trade_executor.execute_entry_with_stop_loss(
            symbol=symbol,
            qty=float(qty),
            side=side,
            entry_price=float(entry_price) if entry_price else None,
            stop_loss_price=float(stop_loss_price),
            take_profit_price=float(take_profit_price) if take_profit_price else None,
            use_market_order=use_market_order
        )
        
        if result.get('success', False):
            # Add to portfolio tracker
            entry_order = result.get('entry_order')
            
            if entry_order:
                trade = Trade(
                    trade_id=str(uuid.uuid4()),
                    symbol=symbol,
                    side=side,
                    entry_date=datetime.datetime.now(),
                    entry_price=entry_order.get('filled_avg_price') or entry_order.get('limit_price') or entry_order.get('stop_price') or 0.0,
                    entry_order_id=entry_order.get('id'),
                    qty=float(qty),
                    stop_loss_price=float(stop_loss_price),
                    take_profit_price=float(take_profit_price) if take_profit_price else None,
                    strategy=strategy,
                    tags=tags,
                    notes=notes
                )
                portfolio_tracker.add_trade(trade)
                result['trade_id'] = trade.trade_id
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error executing entry with stop: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/trades', methods=['GET'])
def get_trades():
    """Get trade history"""
    try:
        symbol = request.args.get('symbol')
        is_open_str = request.args.get('is_open')
        
        # Convert is_open to boolean if provided
        is_open = None
        if is_open_str is not None:
            is_open = is_open_str.lower() in ['true', '1', 't', 'y', 'yes']
        
        trades = portfolio_tracker.get_trades(symbol=symbol, is_open=is_open)
        
        return jsonify({
            'success': True,
            'trades': [trade.to_dict() for trade in trades]
        })
    except Exception as e:
        logger.error(f"Error getting trades: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/trade/<trade_id>', methods=['GET'])
def get_trade(trade_id):
    """Get specific trade"""
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

@broker_bp.route('/trade/<trade_id>/update', methods=['POST'])
def update_trade(trade_id):
    """Update a trade"""
    try:
        data = request.json
        
        # Handle exit information
        if 'exit_price' in data:
            exit_price = float(data['exit_price'])
            exit_date = datetime.datetime.fromisoformat(data.get('exit_date', datetime.datetime.now().isoformat()))
            exit_order_id = data.get('exit_order_id', 'manual-exit')
            
            result = portfolio_tracker.update_trade(
                trade_id,
                exit_date=exit_date,
                exit_price=exit_price,
                exit_order_id=exit_order_id
            )
        else:
            # Update other fields
            result = portfolio_tracker.update_trade(trade_id, **data)
        
        if result:
            return jsonify({
                'success': True,
                'trade': portfolio_tracker.get_trade(trade_id).to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to update trade {trade_id}'
            }), 400
    except Exception as e:
        logger.error(f"Error updating trade: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/performance', methods=['GET'])
def get_performance():
    """Get portfolio performance metrics"""
    try:
        metrics = portfolio_tracker.get_performance_metrics()
        daily_pnl = portfolio_tracker.get_daily_pnl()
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'daily_pnl': daily_pnl
        })
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broker_bp.route('/trades/export', methods=['POST'])
def export_trades():
    """Export trades to CSV"""
    try:
        data = request.json
        filepath = data.get('filepath', 'trade_export.csv')
        
        result = portfolio_tracker.export_trades_to_csv(filepath)
        
        return jsonify({
            'success': result,
            'message': f'Trades exported to {filepath}' if result else 'Failed to export trades'
        })
    except Exception as e:
        logger.error(f"Error exporting trades: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def register_routes(app):
    """Register broker routes with Flask app"""
    app.register_blueprint(broker_bp)
    logger.info("Registered broker routes") 