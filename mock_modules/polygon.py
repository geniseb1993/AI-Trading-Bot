"""
Mock implementation of the polygon-api-client module.
This provides mock classes for the Polygon.io API client.
"""

class RESTClient:
    def __init__(self, api_key=None, use_polygon_cache=False):
        self.api_key = api_key
        self.use_polygon_cache = use_polygon_cache
        
    def stocks_equities_aggregates(self, ticker, multiplier, timespan, from_date, to_date, adjusted=True, limit=5000):
        """Mock implementation of aggregates endpoint"""
        import random
        from datetime import datetime, timedelta
        
        # Parse from_date and to_date to calculate number of data points
        try:
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            to_dt = datetime.strptime(to_date, '%Y-%m-%d')
            days_diff = (to_dt - from_dt).days
            num_points = min(days_diff, limit)
        except:
            num_points = 30
        
        # Generate mock data
        results = []
        base_price = 100.0
        
        for i in range(num_points):
            price_change = (random.random() - 0.5) * 2.0  # -1% to +1%
            close_price = base_price * (1 + price_change/100)
            open_price = close_price * (1 + (random.random() - 0.5) / 100)
            high_price = max(open_price, close_price) * (1 + random.random() / 100)
            low_price = min(open_price, close_price) * (1 - random.random() / 100)
            volume = int(random.random() * 1000000) + 100000
            
            result = {
                'o': open_price,
                'h': high_price,
                'l': low_price,
                'c': close_price,
                'v': volume,
                't': 1600000000000 + i * 86400000,  # Unix timestamp in milliseconds
            }
            
            results.append(result)
            base_price = close_price
        
        return {
            'ticker': ticker,
            'status': 'OK',
            'adjusted': adjusted,
            'queryCount': len(results),
            'resultsCount': len(results),
            'results': results
        }
    
    def reference_tickers(self, search=None, market=None, limit=100):
        """Mock implementation of tickers endpoint"""
        mock_tickers = [
            {'ticker': 'AAPL', 'name': 'Apple Inc.', 'market': 'stocks', 'locale': 'us'},
            {'ticker': 'MSFT', 'name': 'Microsoft Corporation', 'market': 'stocks', 'locale': 'us'},
            {'ticker': 'GOOGL', 'name': 'Alphabet Inc.', 'market': 'stocks', 'locale': 'us'},
            {'ticker': 'AMZN', 'name': 'Amazon.com Inc.', 'market': 'stocks', 'locale': 'us'},
            {'ticker': 'TSLA', 'name': 'Tesla, Inc.', 'market': 'stocks', 'locale': 'us'},
            {'ticker': 'SPY', 'name': 'SPDR S&P 500 ETF Trust', 'market': 'stocks', 'locale': 'us'},
            {'ticker': 'QQQ', 'name': 'Invesco QQQ Trust', 'market': 'stocks', 'locale': 'us'},
        ]
        
        # Filter by search term
        if search:
            search = search.upper()
            results = [ticker for ticker in mock_tickers if search in ticker['ticker'] or search in ticker['name'].upper()]
        else:
            results = mock_tickers
            
        # Filter by market
        if market:
            results = [ticker for ticker in results if ticker['market'] == market]
            
        return {
            'status': 'OK',
            'count': len(results),
            'results': results[:limit]
        }
    
    def stocks_equities_daily_open_close(self, symbol, date):
        """Mock implementation of daily open/close endpoint"""
        import random
        
        base_price = 100.0 + hash(symbol) % 200  # Use hash of symbol to get consistent price
        
        open_price = base_price * (1 + (random.random() - 0.5) / 10)
        close_price = open_price * (1 + (random.random() - 0.5) / 5)
        high_price = max(open_price, close_price) * (1 + random.random() / 20)
        low_price = min(open_price, close_price) * (1 - random.random() / 20)
        volume = int(random.random() * 5000000) + 1000000
        
        return {
            'status': 'OK',
            'from': date,
            'symbol': symbol,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume,
        } 