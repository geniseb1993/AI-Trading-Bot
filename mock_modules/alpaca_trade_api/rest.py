"""
Mock REST API for Alpaca
"""
import logging

logger = logging.getLogger(__name__)

class REST:
    def __init__(self, key_id=None, secret_key=None, base_url=None, api_version=None, **kwargs):
        self.key_id = key_id
        self.secret_key = secret_key
        self.base_url = base_url
        self.api_version = api_version
        self.session = None
        logger.info("Mock Alpaca REST API initialized")
    
    def get_account(self):
        """Get account information"""
        return {
            'id': 'mock-account-id',
            'status': 'ACTIVE',
            'equity': '100000',
            'cash': '100000',
            'buying_power': '100000',
            'portfolio_value': '100000'
        }
    
    def list_positions(self):
        """List current positions"""
        return []
    
    def list_orders(self, status=None, limit=None, after=None, until=None, direction=None, nested=None):
        """List orders"""
        return []
    
    def get_bars(self, symbol, timeframe, start=None, end=None, limit=None, adjustment='raw'):
        """Get historical bars"""
        return []
    
    def submit_order(self, symbol, qty=None, side=None, type='market', time_in_force='day', 
                    limit_price=None, stop_price=None, client_order_id=None, extended_hours=None,
                    order_class=None, take_profit=None, stop_loss=None, notional=None):
        """Submit a new order"""
        return {
            'id': 'mock-order-id',
            'client_order_id': client_order_id or 'mock-client-order-id',
            'symbol': symbol,
            'side': side,
            'type': type,
            'status': 'accepted'
        }
    
    def get_order(self, order_id):
        """Get order by ID"""
        return {
            'id': order_id,
            'status': 'filled'
        }

    def cancel_order(self, order_id):
        """Cancel order by ID"""
        return {
            'id': order_id,
            'status': 'canceled'
        } 