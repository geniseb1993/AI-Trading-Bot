"""
Mock implementation of the alpaca_trade_api module.
This provides mock classes for the Alpaca API client.
"""

import random
from datetime import datetime, timedelta

class REST:
    def __init__(self, key_id=None, secret_key=None, base_url=None, api_version=None):
        self.key_id = key_id
        self.secret_key = secret_key
        self.base_url = base_url
        self.api_version = api_version
        self.account = Account()
        self.positions = Positions()
        self.orders = Orders()
        
    def get_account(self):
        """Get the account information"""
        return self.account
        
    def list_positions(self):
        """List all positions"""
        return self.positions.list()
        
    def get_position(self, symbol):
        """Get a specific position"""
        return self.positions.get(symbol)
        
    def list_orders(self, status=None, limit=None, after=None, until=None, direction=None):
        """List orders based on parameters"""
        return self.orders.list(status, limit)
        
    def submit_order(self, symbol, qty=None, side=None, type=None, time_in_force=None, 
                    limit_price=None, stop_price=None, client_order_id=None, notional=None):
        """Submit a new order"""
        return self.orders.submit(symbol, qty, side, type, time_in_force, limit_price,
                                  stop_price, client_order_id, notional)
        
    def get_bars(self, symbol, timeframe, start=None, end=None, limit=None):
        """Get bars for a symbol"""
        bars = []
        now = datetime.now()
        
        # Number of bars to generate
        num_bars = limit if limit else 100
        
        # Base price depends on symbol to maintain consistency
        base_price = 100.0 + sum(ord(c) for c in symbol) % 300
        
        # Generate random bars
        for i in range(num_bars):
            bar_time = now - timedelta(minutes=i * self._timeframe_to_minutes(timeframe))
            price_change = (random.random() - 0.45) * 2.0  # Slight upward bias
            close_price = base_price * (1 + price_change/100)
            open_price = base_price * (1 + (random.random() - 0.5) / 100)
            high_price = max(open_price, close_price) * (1 + random.random() / 100)
            low_price = min(open_price, close_price) * (1 - random.random() / 100)
            volume = int(random.random() * 1000000) + 100000
            
            bar = {
                't': bar_time,
                'o': round(open_price, 2),
                'h': round(high_price, 2),
                'l': round(low_price, 2),
                'c': round(close_price, 2),
                'v': volume,
                'n': random.randint(100, 1000),  # Number of trades
                'vw': round((high_price + low_price + close_price) / 3, 2)  # Volume weighted average price
            }
            
            bars.append(Bar(bar))
            base_price = close_price
            
        return bars
    
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