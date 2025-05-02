"""
Mock implementation of the alpaca_trade_api module.
This provides mock classes for the Alpaca API client.
"""

import random
from datetime import datetime, timedelta

class REST:
    def __init__(self, key_id='', secret_key='', base_url='', api_version='v2'):
        self.key_id = key_id
        self.secret_key = secret_key
        self.base_url = base_url
        self.api_version = api_version
        print("Mock Alpaca REST API initialized")
        self.account = Account()
        self.positions = Positions()
        self.orders = Orders()
        
    def get_account(self):
        """Get the account information"""
        return {
            'account_number': 'MOCK',
            'buying_power': '100000',
            'cash': '100000',
            'equity': '100000',
            'status': 'ACTIVE'
        }
        
    def list_positions(self):
        """List all positions"""
        return []
        
    def get_position(self, symbol):
        """Get a specific position"""
        return self.positions.get(symbol)
        
    def list_orders(self, status='open'):
        """List orders based on parameters"""
        return []
        
    def submit_order(self, symbol, qty, side, type, time_in_force, limit_price=None, stop_price=None):
        """Submit a new order"""
        return {
            'id': 'mock-order-id',
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'type': type,
            'time_in_force': time_in_force,
            'status': 'accepted'
        }
        
    def get_barset(self, symbols, timeframe, limit=None, start=None, end=None, after=None, until=None):
        if isinstance(symbols, str):
            symbols = [symbols]
            
        return MockBarset({symbol: [] for symbol in symbols})
    
    def get_bars(self, symbols, timeframe, start=None, end=None, limit=None):
        """Get bars for a symbol"""
        if isinstance(symbols, str):
            symbols = [symbols]
            
        return [MockBar(symbol) for symbol in symbols]
    
    def _timeframe_to_minutes(self, timeframe):
        """Convert timeframe string to minutes"""
        if timeframe.endswith('Min'):
            return int(timeframe[:-3])
        elif timeframe.endswith('Hour'):
            return int(timeframe[:-4]) * 60
        elif timeframe.endswith('Day'):
            return int(timeframe[:-3]) * 60 * 24
        return 1  # Default to 1 minute


class Account:
    def __init__(self):
        self.id = 'mock-account-id'
        self.account_number = 'MOCK-ACCOUNT'
        self.status = 'ACTIVE'
        self.currency = 'USD'
        self.cash = 100000.0
        self.portfolio_value = 150000.0
        self.equity = 150000.0
        self.buying_power = 300000.0
        self.initial_margin = 0.0
        self.maintenance_margin = 0.0
        self.daytrading_buying_power = 600000.0
        self.last_equity = 145000.0
        self.last_maintenance_margin = 0.0
        self.created_at = datetime.now() - timedelta(days=30)
        

class Positions:
    def __init__(self):
        self.positions = [
            {
                'symbol': 'AAPL',
                'qty': 10,
                'avg_entry_price': 175.50,
                'market_value': 1800.0,
                'side': 'long',
                'unrealized_pl': 45.0,
                'unrealized_plpc': 0.025,
                'current_price': 180.0
            },
            {
                'symbol': 'MSFT',
                'qty': 5,
                'avg_entry_price': 350.25,
                'market_value': 1800.0,
                'side': 'long',
                'unrealized_pl': 24.75,
                'unrealized_plpc': 0.014,
                'current_price': 355.20
            }
        ]
        
    def list(self):
        """Return list of positions"""
        return [Position(p) for p in self.positions]
    
    def get(self, symbol):
        """Get a specific position"""
        for p in self.positions:
            if p['symbol'] == symbol:
                return Position(p)
        return None


class Orders:
    def __init__(self):
        self.orders = [
            {
                'id': 'mock-order-1',
                'client_order_id': 'mock-client-1',
                'created_at': datetime.now() - timedelta(hours=2),
                'updated_at': datetime.now() - timedelta(hours=1),
                'submitted_at': datetime.now() - timedelta(hours=2),
                'filled_at': datetime.now() - timedelta(hours=1),
                'expired_at': None,
                'canceled_at': None,
                'failed_at': None,
                'asset_id': 'AAPL',
                'symbol': 'AAPL',
                'asset_class': 'us_equity',
                'qty': 10,
                'filled_qty': 10,
                'type': 'market',
                'side': 'buy',
                'time_in_force': 'day',
                'limit_price': None,
                'stop_price': None,
                'filled_avg_price': 175.50,
                'status': 'filled'
            }
        ]
        
    def list(self, status=None, limit=None):
        """Return list of orders filtered by status"""
        result = self.orders
        if status:
            result = [o for o in result if o['status'] == status]
        if limit:
            result = result[:limit]
        return [Order(o) for o in result]
    
    def submit(self, symbol, qty=None, side=None, type=None, time_in_force=None, 
               limit_price=None, stop_price=None, client_order_id=None, notional=None):
        """Submit a new order"""
        price = 100.0 + sum(ord(c) for c in symbol) % 300
        order_id = f"mock-order-{random.randint(1000, 9999)}"
        client_id = client_order_id or f"mock-client-{random.randint(1000, 9999)}"
        now = datetime.now()
        
        order = {
            'id': order_id,
            'client_order_id': client_id,
            'created_at': now,
            'updated_at': now,
            'submitted_at': now,
            'filled_at': None,
            'expired_at': None,
            'canceled_at': None,
            'failed_at': None,
            'asset_id': symbol,
            'symbol': symbol,
            'asset_class': 'us_equity',
            'qty': qty,
            'filled_qty': 0,
            'type': type or 'market',
            'side': side or 'buy',
            'time_in_force': time_in_force or 'day',
            'limit_price': limit_price,
            'stop_price': stop_price,
            'filled_avg_price': None,
            'status': 'new'
        }
        
        self.orders.append(order)
        return Order(order)


class Position:
    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)
            
    def __str__(self):
        return f"Position(symbol={self.symbol}, qty={self.qty}, side={self.side})"


class Order:
    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)
            
    def __str__(self):
        return f"Order(id={self.id}, symbol={self.symbol}, side={self.side}, status={self.status})"


class Bar:
    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)
            
    def __str__(self):
        return f"Bar(time={self.t}, open={self.o}, high={self.h}, low={self.l}, close={self.c})"


class StreamConn:
    def __init__(self, key_id='', secret_key='', base_url='', data_stream=''):
        self.key_id = key_id
        self.secret_key = secret_key
        self.base_url = base_url
        self.data_stream = data_stream
        self.handlers = {}
        print("Mock Alpaca StreamConn initialized")
    
    def on(self, event_name):
        def decorator(func):
            self.handlers[event_name] = func
            return func
        return decorator
    
    def run(self):
        print("Mock StreamConn running")
        pass


class MockBarset(dict):
    def __iter__(self):
        return iter(self.keys())
    
    def df(self):
        import pandas as pd
        return pd.DataFrame()


class MockBar:
    def __init__(self, symbol):
        import time
        import random
        self.symbol = symbol
        self.t = time.time()
        self.o = random.uniform(100, 200)
        self.h = self.o * (1 + random.uniform(0, 0.05))
        self.l = self.o * (1 - random.uniform(0, 0.05))
        self.c = random.uniform(self.l, self.h)
        self.v = random.randint(1000, 10000)


class Trade:
    @staticmethod
    def submit_order(symbol, qty, side, type, time_in_force, limit_price=None, stop_price=None):
        return {
            'id': 'mock-order-id',
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'type': type,
            'time_in_force': time_in_force,
            'status': 'accepted'
        }

tradeapi = Trade 