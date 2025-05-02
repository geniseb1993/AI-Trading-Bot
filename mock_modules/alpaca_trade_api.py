"""
Mock implementation of the alpaca_trade_api module for development and testing.
This simpler version avoids external dependencies like pandas and numpy.
"""
import datetime
import random
import json
import os

class REST:
    def __init__(self, key_id='', secret_key='', base_url='', api_version='v2'):
        self.key_id = key_id
        self.secret_key = secret_key
        self.base_url = base_url
        self.api_version = api_version
        print("Mock Alpaca REST API initialized")
    
    def get_account(self):
        """Get account information"""
        return {
            'id': 'mock-account-id',
            'account_number': 'mock-account-number',
            'status': 'ACTIVE',
            'currency': 'USD',
            'buying_power': '100000.00',
            'cash': '100000.00',
            'portfolio_value': '150000.00',
            'equity': '150000.00'
        }
    
    def list_positions(self):
        """List all positions"""
        return [
            {
                'symbol': 'AAPL',
                'qty': 10,
                'avg_entry_price': 150.0,
                'market_value': 1600.0,
                'current_price': 160.0,
                'unrealized_pl': 100.0,
                'unrealized_plpc': 0.0667,
                'side': 'long'
            },
            {
                'symbol': 'MSFT',
                'qty': 5,
                'avg_entry_price': 300.0,
                'market_value': 1550.0,
                'current_price': 310.0,
                'unrealized_pl': 50.0,
                'unrealized_plpc': 0.0333,
                'side': 'long'
            }
        ]
    
    def get_position(self, symbol):
        """Get a specific position"""
        positions = self.list_positions()
        for position in positions:
            if position['symbol'] == symbol:
                return position
        return None
    
    def list_orders(self, status='open'):
        """List all orders with the given status"""
        orders = [
            {
                'id': 'mock-order-1',
                'client_order_id': 'client-mock-order-1',
                'symbol': 'AAPL',
                'qty': 5,
                'side': 'buy',
                'type': 'market',
                'time_in_force': 'day',
                'status': 'filled',
                'filled_qty': 5,
                'filled_avg_price': 150.0,
                'created_at': '2023-01-01T12:00:00Z',
                'updated_at': '2023-01-01T12:01:00Z',
                'submitted_at': '2023-01-01T12:00:00Z',
                'filled_at': '2023-01-01T12:01:00Z'
            },
            {
                'id': 'mock-order-2',
                'client_order_id': 'client-mock-order-2',
                'symbol': 'MSFT',
                'qty': 10,
                'side': 'buy',
                'type': 'limit',
                'limit_price': 300.0,
                'time_in_force': 'day',
                'status': 'open',
                'filled_qty': 0,
                'created_at': '2023-01-02T12:00:00Z',
                'updated_at': '2023-01-02T12:00:00Z',
                'submitted_at': '2023-01-02T12:00:00Z'
            }
        ]
        return [order for order in orders if order['status'] == status]
    
    def submit_order(self, symbol, qty, side, type, time_in_force, limit_price=None, stop_price=None):
        """Submit a new order"""
        return {
            'id': f'mock-order-{random.randint(1000, 9999)}',
            'client_order_id': f'client-mock-order-{random.randint(1000, 9999)}',
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'type': type,
            'time_in_force': time_in_force,
            'status': 'accepted'
        }
    
    def get_barset(self, symbols, timeframe, limit=None, start=None, end=None, after=None, until=None):
        """Get historical bars for a symbol or symbols (deprecated method)"""
        result = {}
        for symbol in symbols:
            result[symbol] = [MockBar(symbol) for _ in range(limit or 100)]
        return MockBarset(result)
    
    def get_bars(self, symbols, timeframe, start=None, end=None, limit=None):
        """Get historical bars for a symbol or symbols"""
        bars = []
        for i in range(limit or 100):
            for symbol in symbols:
                timestamp = datetime.datetime.now() - datetime.timedelta(minutes=i)
                close_price = 100 + random.random() * 10
                bars.append({
                    't': timestamp.isoformat(),
                    'o': close_price - random.random() * 1,
                    'h': close_price + random.random() * 1,
                    'l': close_price - random.random() * 1.5,
                    'c': close_price,
                    'v': int(random.random() * 1000000),
                    'symbol': symbol
                })
        return bars

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
        """Pretend to start the connection"""
        print("Mock StreamConn running")

class MockBarset(dict):
    def __iter__(self):
        return iter(self.keys())
    
    def df(self):
        """Return a dict instead of a pandas DataFrame"""
        data = []
        for symbol, bars in self.items():
            for bar in bars:
                data.append({
                    'symbol': symbol,
                    'time': bar.t,
                    'open': bar.o,
                    'high': bar.h,
                    'low': bar.l,
                    'close': bar.c,
                    'volume': bar.v
                })
        return data

class MockBar:
    def __init__(self, symbol):
        self.symbol = symbol
        timestamp = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))
        close_price = 100 + random.random() * 10
        self.t = timestamp
        self.o = close_price - random.random() * 1
        self.h = close_price + random.random() * 1
        self.l = close_price - random.random() * 1.5
        self.c = close_price
        self.v = int(random.random() * 1000000)

class Trade:
    @staticmethod
    def submit_order(symbol, qty, side, type, time_in_force, limit_price=None, stop_price=None):
        """Submit an order (static method)"""
        rest = REST()
        return rest.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type=type,
            time_in_force=time_in_force,
            limit_price=limit_price,
            stop_price=stop_price
        )

tradeapi = Trade 