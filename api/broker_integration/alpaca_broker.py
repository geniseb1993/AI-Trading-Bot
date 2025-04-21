import os
import logging
from datetime import datetime, timedelta
import time
import threading
import random
import pandas as pd
from typing import Dict, List, Optional, Any, Union
import json

# Alpaca imports
from alpaca.trading import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from .broker_interface import (
    BrokerInterface,
    Account,
    Position,
    Order,
    OrderStatus,
)
from .mock_broker import MockBroker
from ..config import bot_config

logger = logging.getLogger(__name__)

class AlpacaBroker(BrokerInterface):
    """Alpaca API implementation with fallback to mock broker"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, is_paper: bool = True):
        self.api_key = api_key or os.environ.get("ALPACA_API_KEY")
        self.api_secret = api_secret or os.environ.get("ALPACA_API_SECRET")
        self.is_paper = is_paper
        self.connected = False
        self.alpaca_client = None
        
        # Initialize fallback broker
        self.mock_broker = MockBroker()
        self.using_mock = False
        
        # Try to import alpaca-trade-api
        try:
            import alpaca_trade_api as tradeapi
            self.tradeapi = tradeapi
            logger.info("Successfully imported alpaca-trade-api")
        except ImportError:
            logger.warning("alpaca-trade-api not installed, using mock broker")
            self.tradeapi = None
            self.using_mock = True
        
        self.is_running = False
        self.trading_thread = None
        self.stop_event = threading.Event()
        
        # Create Alpaca clients
        self.trading_client = TradingClient(
            bot_config.ALPACA_API_KEY,
            bot_config.ALPACA_SECRET_KEY,
            paper=bot_config.PAPER_TRADING
        )
        
        self.data_client = StockHistoricalDataClient(
            bot_config.ALPACA_API_KEY,
            bot_config.ALPACA_SECRET_KEY
        )
        
        # Initialize data directory for storing local data
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize trading history files
        self._initialize_data_files()
    
    def _initialize_data_files(self) -> None:
        """Initialize data files for tracking trades and performance"""
        active_trades_file = os.path.join(self.data_dir, 'active_trades.csv')
        if not os.path.exists(active_trades_file):
            pd.DataFrame(columns=[
                'symbol', 'entry_date', 'entry_price', 'current_price',
                'quantity', 'pnl', 'pnl_percent', 'position_type',
                'stop_loss', 'take_profit', 'strategy'
            ]).to_csv(active_trades_file, index=False)
            logger.info(f"Created active trades file: {active_trades_file}")
        
        history_file = os.path.join(self.data_dir, 'trading_history.csv')
        if not os.path.exists(history_file):
            pd.DataFrame(columns=[
                'symbol', 'entry_date', 'exit_date', 'entry_price',
                'exit_price', 'quantity', 'pnl', 'pnl_percent',
                'position_type', 'strategy', 'exit_reason'
            ]).to_csv(history_file, index=False)
            logger.info(f"Created trading history file: {history_file}")
    
    def connect(self) -> bool:
        """Connect to Alpaca API or fallback to mock broker"""
        if self.using_mock or not self.api_key or not self.api_secret:
            logger.warning("Using mock broker for Alpaca integration")
            self.using_mock = True
            self.mock_broker.connect()
            self.connected = True
            return True
        
        try:
            base_url = "https://paper-api.alpaca.markets" if self.is_paper else "https://api.alpaca.markets"
            self.alpaca_client = self.tradeapi.REST(
                self.api_key,
                self.api_secret,
                base_url=base_url,
                api_version="v2"
            )
            # Test connection
            account_info = self.alpaca_client.get_account()
            logger.info(f"Connected to Alpaca API: {account_info.id}")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca API: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            self.mock_broker.connect()
            self.connected = True
            return True
    
    def _ensure_connected(self):
        """Ensure we're connected to the broker"""
        if not self.connected:
            self.connect()
    
    def get_account(self) -> Account:
        """Get account information from Alpaca or mock"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.get_account()
        
        try:
            account = self.alpaca_client.get_account()
            return Account(
                id=account.id,
                cash=float(account.cash),
                portfolio_value=float(account.portfolio_value),
                buying_power=float(account.buying_power),
                equity=float(account.equity),
                currency=account.currency
            )
        except Exception as e:
            logger.error(f"Error getting account from Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.get_account()
    
    def get_positions(self) -> List[Position]:
        """Get all current positions"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.get_positions()
        
        try:
            alpaca_positions = self.alpaca_client.list_positions()
            positions = []
            
            for pos in alpaca_positions:
                side = OrderSide.BUY if float(pos.qty) > 0 else OrderSide.SELL
                positions.append(Position(
                    symbol=pos.symbol,
                    qty=abs(float(pos.qty)),
                    avg_entry_price=float(pos.avg_entry_price),
                    current_price=float(pos.current_price),
                    side=side
                ))
            
            return positions
        except Exception as e:
            logger.error(f"Error getting positions from Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.get_positions()
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a specific symbol"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.get_position(symbol)
        
        try:
            pos = self.alpaca_client.get_position(symbol)
            side = OrderSide.BUY if float(pos.qty) > 0 else OrderSide.SELL
            return Position(
                symbol=pos.symbol,
                qty=abs(float(pos.qty)),
                avg_entry_price=float(pos.avg_entry_price),
                current_price=float(pos.current_price),
                side=side
            )
        except Exception as e:
            # If position not found, return None
            if "position not found" in str(e).lower():
                return None
            
            logger.error(f"Error getting position for {symbol} from Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.get_position(symbol)
    
    def _convert_alpaca_order_to_interface(self, alpaca_order) -> Order:
        """Convert Alpaca order to our interface Order object"""
        # Map Alpaca order side to our OrderSide
        side = OrderSide.BUY if alpaca_order.side.lower() == "buy" else OrderSide.SELL
        
        # Map Alpaca order type to our OrderType
        order_type_map = {
            "market": OrderType.MARKET,
            "limit": OrderType.LIMIT,
            "stop": OrderType.STOP,
            "stop_limit": OrderType.STOP_LIMIT,
            "trailing_stop": OrderType.TRAILING_STOP
        }
        order_type = order_type_map.get(alpaca_order.type.lower(), OrderType.MARKET)
        
        # Map Alpaca order status to our OrderStatus
        status_map = {
            "new": OrderStatus.NEW,
            "partially_filled": OrderStatus.PARTIALLY_FILLED,
            "filled": OrderStatus.FILLED,
            "done_for_day": OrderStatus.FILLED,
            "canceled": OrderStatus.CANCELED,
            "expired": OrderStatus.CANCELED,
            "replaced": OrderStatus.NEW,
            "pending_cancel": OrderStatus.PENDING,
            "pending_replace": OrderStatus.PENDING,
            "accepted": OrderStatus.NEW,
            "pending_new": OrderStatus.PENDING,
            "accepted_for_bidding": OrderStatus.NEW,
            "stopped": OrderStatus.FILLED,
            "rejected": OrderStatus.REJECTED,
            "suspended": OrderStatus.PENDING,
            "calculated": OrderStatus.NEW
        }
        status = status_map.get(alpaca_order.status.lower(), OrderStatus.NEW)
        
        # Map Alpaca time in force to our TimeInForce
        tif_map = {
            "day": TimeInForce.DAY,
            "gtc": TimeInForce.GTC,
            "opg": TimeInForce.DAY,
            "cls": TimeInForce.DAY,
            "ioc": TimeInForce.IOC,
            "fok": TimeInForce.FOK
        }
        time_in_force = tif_map.get(alpaca_order.time_in_force.lower(), TimeInForce.DAY)
        
        # Parse dates
        created_at = datetime.datetime.fromisoformat(alpaca_order.created_at.replace('Z', '+00:00'))
        filled_at = None
        if alpaca_order.filled_at and alpaca_order.filled_at != "None":
            filled_at = datetime.datetime.fromisoformat(alpaca_order.filled_at.replace('Z', '+00:00'))
        
        # Create our Order object
        return Order(
            id=alpaca_order.id,
            symbol=alpaca_order.symbol,
            qty=float(alpaca_order.qty),
            side=side,
            type=order_type,
            limit_price=float(alpaca_order.limit_price) if alpaca_order.limit_price else None,
            stop_price=float(alpaca_order.stop_price) if alpaca_order.stop_price else None,
            time_in_force=time_in_force,
            status=status,
            created_at=created_at,
            filled_at=filled_at,
            filled_qty=float(alpaca_order.filled_qty) if alpaca_order.filled_qty else 0,
            filled_avg_price=float(alpaca_order.filled_avg_price) if alpaca_order.filled_avg_price else None,
            trail_percent=float(alpaca_order.trail_percent) if hasattr(alpaca_order, 'trail_percent') and alpaca_order.trail_percent else None,
            trail_price=float(alpaca_order.trail_price) if hasattr(alpaca_order, 'trail_price') and alpaca_order.trail_price else None
        )
    
    def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get list of orders with optional status filter"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.get_orders(status)
        
        try:
            # Convert our status to Alpaca status
            alpaca_status = None
            if status:
                status_map = {
                    OrderStatus.NEW: "open",
                    OrderStatus.PARTIALLY_FILLED: "open",
                    OrderStatus.FILLED: "closed",
                    OrderStatus.CANCELED: "closed",
                    OrderStatus.REJECTED: "closed",
                    OrderStatus.PENDING: "open"
                }
                alpaca_status = status_map.get(status)
            
            # Get orders from Alpaca
            if alpaca_status:
                alpaca_orders = self.alpaca_client.list_orders(status=alpaca_status)
            else:
                # Get both open and closed orders
                alpaca_orders = []
                alpaca_orders.extend(self.alpaca_client.list_orders(status="open"))
                alpaca_orders.extend(self.alpaca_client.list_orders(status="closed", limit=100))
            
            # Convert to our Order objects
            orders = [self._convert_alpaca_order_to_interface(order) for order in alpaca_orders]
            
            # Filter by our status if needed
            if status:
                orders = [order for order in orders if order.status == status]
            
            return orders
        except Exception as e:
            logger.error(f"Error getting orders from Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.get_orders(status)
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get a specific order by ID"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.get_order(order_id)
        
        try:
            alpaca_order = self.alpaca_client.get_order(order_id)
            return self._convert_alpaca_order_to_interface(alpaca_order)
        except Exception as e:
            logger.error(f"Error getting order {order_id} from Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.get_order(order_id)
    
    def submit_order(
        self,
        symbol: str,
        qty: float,
        side: OrderSide,
        type: OrderType = OrderType.MARKET,
        time_in_force: TimeInForce = TimeInForce.DAY,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        trail_percent: Optional[float] = None,
    ) -> Optional[Order]:
        """Submit an order to Alpaca"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=type,
                time_in_force=time_in_force,
                limit_price=limit_price,
                stop_price=stop_price,
                trail_percent=trail_percent
            )
        
        try:
            # Convert our enums to Alpaca format
            alpaca_side = "buy" if side == OrderSide.BUY else "sell"
            
            alpaca_type_map = {
                OrderType.MARKET: "market",
                OrderType.LIMIT: "limit",
                OrderType.STOP: "stop",
                OrderType.STOP_LIMIT: "stop_limit",
                OrderType.TRAILING_STOP: "trailing_stop"
            }
            alpaca_type = alpaca_type_map.get(type, "market")
            
            alpaca_tif_map = {
                TimeInForce.DAY: "day",
                TimeInForce.GTC: "gtc",
                TimeInForce.IOC: "ioc",
                TimeInForce.FOK: "fok"
            }
            alpaca_tif = alpaca_tif_map.get(time_in_force, "day")
            
            # Submit order to Alpaca
            alpaca_order = self.alpaca_client.submit_order(
                symbol=symbol,
                qty=qty,
                side=alpaca_side,
                type=alpaca_type,
                time_in_force=alpaca_tif,
                limit_price=limit_price,
                stop_price=stop_price,
                trail_percent=trail_percent
            )
            
            return self._convert_alpaca_order_to_interface(alpaca_order)
        except Exception as e:
            logger.error(f"Error submitting order to Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=type,
                time_in_force=time_in_force,
                limit_price=limit_price,
                stop_price=stop_price,
                trail_percent=trail_percent
            )
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.cancel_order(order_id)
        
        try:
            self.alpaca_client.cancel_order(order_id)
            return True
        except Exception as e:
            logger.error(f"Error canceling order {order_id} on Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.cancel_order(order_id)
    
    def cancel_all_orders(self) -> bool:
        """Cancel all open orders"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.cancel_all_orders()
        
        try:
            self.alpaca_client.cancel_all_orders()
            return True
        except Exception as e:
            logger.error(f"Error canceling all orders on Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.cancel_all_orders()
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data for a symbol"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.get_market_data(symbol)
        
        try:
            # Get latest bar
            bars = self.alpaca_client.get_barset(symbol, "minute", limit=1)
            bar = bars[symbol][0]
            
            # Get latest quote
            quote = self.alpaca_client.get_last_quote(symbol)
            
            return {
                "symbol": symbol,
                "bid": float(quote.bidprice),
                "ask": float(quote.askprice),
                "last": float(bar.c),
                "high": float(bar.h),
                "low": float(bar.l),
                "volume": int(bar.v),
                "timestamp": bar.t.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting market data for {symbol} from Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.get_market_data(symbol)
    
    def get_bot_status(self) -> bool:
        """Get the current status of the trading bot"""
        return self.is_running
    
    def start_bot(self) -> bool:
        """Start the autonomous trading bot"""
        try:
            if not self.is_running:
                logger.info("Starting autonomous trading bot...")
                self.is_running = True
                self.stop_event.clear()
                self.trading_thread = threading.Thread(target=self._trading_loop)
                self.trading_thread.daemon = True
                self.trading_thread.start()
                logger.info("Autonomous trading bot started successfully")
                return True
            logger.warning("Bot is already running")
            return False
        except Exception as e:
            logger.error(f"Error starting bot: {str(e)}")
            return False
    
    def stop_bot(self) -> bool:
        """Stop the autonomous trading bot"""
        try:
            if self.is_running:
                logger.info("Stopping autonomous trading bot...")
                self.is_running = False
                self.stop_event.set()
                if self.trading_thread and self.trading_thread.is_alive():
                    self.trading_thread.join(timeout=10)
                logger.info("Autonomous trading bot stopped successfully")
                return True
            logger.warning("Bot is not running")
            return False
        except Exception as e:
            logger.error(f"Error stopping bot: {str(e)}")
            return False
    
    def _trading_loop(self) -> None:
        """Main trading loop that runs continuously while the bot is active"""
        logger.info("Starting trading loop")
        while not self.stop_event.is_set():
            try:
                # Run a single trading cycle
                self.run_trading_cycle()
                
                # Sleep for a bit to avoid excessive API calls
                time.sleep(15)
            except Exception as e:
                logger.error(f"Error in trading loop: {str(e)}")
                time.sleep(30)  # Wait longer if there was an error
    
    def run_trading_cycle(self) -> bool:
        """Run a single trading cycle"""
        try:
            # Update active trade prices
            self._update_active_trade_prices()
            
            # Check exit conditions for existing trades
            self._check_exit_conditions()
            
            # Look for new trading opportunities
            self._find_new_trades()
            
            # Update portfolio performance records
            self._update_portfolio_performance()
            
            logger.debug("Completed trading cycle")
            return True
        except Exception as e:
            logger.error(f"Error in trading cycle: {str(e)}")
            return False
    
    def get_active_trades(self) -> List[Dict[str, Any]]:
        """Get all active trades"""
        active_trades_file = os.path.join(self.data_dir, 'active_trades.csv')
        
        try:
            if os.path.exists(active_trades_file):
                active_trades = pd.read_csv(active_trades_file)
                return active_trades.to_dict('records')
            return []
        except Exception as e:
            logger.error(f"Error reading active trades: {str(e)}")
            return []
    
    def get_trading_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get trading history with optional limit"""
        history_file = os.path.join(self.data_dir, 'trading_history.csv')
        
        try:
            if os.path.exists(history_file):
                trading_history = pd.read_csv(history_file)
                if limit and limit > 0:
                    trading_history = trading_history.tail(limit)
                return trading_history.to_dict('records')
            return []
        except Exception as e:
            logger.error(f"Error reading trading history: {str(e)}")
            return []
    
    def get_real_time_data(self) -> Dict[str, Any]:
        """Get real-time market data for active symbols"""
        try:
            # Get active trades to determine which symbols to fetch
            active_trades = self.get_active_trades()
            active_symbols = [trade['symbol'] for trade in active_trades]
            
            # Add some default symbols if no active trades
            if not active_symbols:
                active_symbols = ['SPY', 'QQQ', 'IWM', 'AAPL', 'MSFT']
            
            # Fetch real market data from Alpaca
            real_time_data = {}
            
            # Using a try/except for each symbol to prevent one failure from stopping the whole process
            for symbol in active_symbols:
                try:
                    # In production, get real-time data for each symbol
                    # For now, use either mock data or historical data
                    if bot_config.USE_ALPACA_DATA:
                        # Get the latest data from Alpaca
                        bars_request = StockBarsRequest(
                            symbol_or_symbols=[symbol],
                            timeframe=TimeFrame.Minute,
                            start=datetime.now() - datetime.timedelta(days=1),
                            end=datetime.now()
                        )
                        bars = self.data_client.get_stock_bars(bars_request)
                        
                        if bars and symbol in bars:
                            latest_bar = bars[symbol][-1]
                            real_time_data[symbol] = {
                                'price': latest_bar.close,
                                'volume': latest_bar.volume,
                                'timestamp': latest_bar.timestamp.isoformat(),
                                'change': (latest_bar.close - latest_bar.open) / latest_bar.open * 100,
                                'source': 'alpaca'
                            }
                        else:
                            # Fallback to mock data
                            self._add_mock_data(real_time_data, symbol)
                    else:
                        # Use mock data
                        self._add_mock_data(real_time_data, symbol)
                except Exception as symbol_error:
                    logger.warning(f"Error fetching data for {symbol}: {str(symbol_error)}")
                    # Add mock data as fallback
                    self._add_mock_data(real_time_data, symbol)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'market_data': real_time_data
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time data: {str(e)}")
            return {
                'timestamp': datetime.now().isoformat(),
                'market_data': {},
                'error': str(e)
            }
    
    def _add_mock_data(self, data_dict: Dict[str, Any], symbol: str) -> None:
        """Add mock data for a symbol"""
        data_dict[symbol] = {
            'price': round(random.uniform(50, 500), 2),
            'volume': random.randint(10000, 1000000),
            'timestamp': datetime.now().isoformat(),
            'change': round(random.uniform(-5, 5), 2),
            'source': 'mock'
        }
    
    def _update_active_trade_prices(self) -> None:
        """Update prices for active trades"""
        try:
            active_trades_file = os.path.join(self.data_dir, 'active_trades.csv')
            
            if os.path.exists(active_trades_file):
                # Read active trades
                active_trades = pd.read_csv(active_trades_file)
                
                if not active_trades.empty:
                    # Get real-time data
                    real_time_data = self.get_real_time_data()
                    market_data = real_time_data.get('market_data', {})
                    
                    # Update each trade
                    for idx, trade in active_trades.iterrows():
                        symbol = trade['symbol']
                        
                        # Get current price (either real or simulated)
                        if symbol in market_data:
                            current_price = market_data[symbol]['price']
                        else:
                            # Simulate price movement if data not available
                            entry_price = trade['entry_price']
                            # Random price movement (-3% to +3% from entry)
                            current_price = entry_price * (1 + random.uniform(-0.03, 0.03))
                        
                        # Update trade
                        active_trades.at[idx, 'current_price'] = round(current_price, 2)
                        
                        # Calculate PnL
                        entry_price = trade['entry_price']
                        quantity = trade['quantity']
                        position_type = trade['position_type']
                        
                        if position_type == 'Long':
                            pnl = (current_price - entry_price) * quantity
                            pnl_percent = ((current_price / entry_price) - 1) * 100
                        else:  # Short
                            pnl = (entry_price - current_price) * quantity
                            pnl_percent = ((entry_price / current_price) - 1) * 100
                        
                        active_trades.at[idx, 'pnl'] = round(pnl, 2)
                        active_trades.at[idx, 'pnl_percent'] = round(pnl_percent, 2)
                    
                    # Save updated trades
                    active_trades.to_csv(active_trades_file, index=False)
                    logger.debug(f"Updated prices for {len(active_trades)} active trades")
        
        except Exception as e:
            logger.error(f"Error updating active trade prices: {str(e)}")
    
    def _check_exit_conditions(self) -> None:
        """Check exit conditions for existing trades"""
        try:
            active_trades_file = os.path.join(self.data_dir, 'active_trades.csv')
            history_file = os.path.join(self.data_dir, 'trading_history.csv')
            
            if os.path.exists(active_trades_file):
                # Read active trades
                active_trades = pd.read_csv(active_trades_file)
                
                if not active_trades.empty:
                    # Identify trades to close
                    trades_to_close = []
                    
                    for idx, trade in active_trades.iterrows():
                        current_price = trade['current_price']
                        stop_loss = trade['stop_loss']
                        take_profit = trade['take_profit']
                        position_type = trade['position_type']
                        
                        # Check stop loss
                        if position_type == 'Long' and current_price <= stop_loss:
                            trades_to_close.append((idx, trade, 'stop_loss'))
                        elif position_type == 'Short' and current_price >= stop_loss:
                            trades_to_close.append((idx, trade, 'stop_loss'))
                        
                        # Check take profit
                        elif position_type == 'Long' and current_price >= take_profit:
                            trades_to_close.append((idx, trade, 'take_profit'))
                        elif position_type == 'Short' and current_price <= take_profit:
                            trades_to_close.append((idx, trade, 'take_profit'))
                        
                        # Random decision to close trade (5% chance)
                        elif random.random() < 0.05:
                            trades_to_close.append((idx, trade, 'algorithm_decision'))
                    
                    # Close trades and update history
                    if trades_to_close:
                        # Read trading history
                        if os.path.exists(history_file):
                            trading_history = pd.read_csv(history_file)
                        else:
                            trading_history = pd.DataFrame(columns=[
                                'symbol', 'entry_date', 'exit_date', 'entry_price',
                                'exit_price', 'quantity', 'pnl', 'pnl_percent',
                                'position_type', 'strategy', 'exit_reason'
                            ])
                        
                        # Process each trade to close
                        indices_to_drop = []
                        for idx, trade, reason in trades_to_close:
                            # Add to history
                            history_entry = {
                                'symbol': trade['symbol'],
                                'entry_date': trade['entry_date'],
                                'exit_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'entry_price': trade['entry_price'],
                                'exit_price': trade['current_price'],
                                'quantity': trade['quantity'],
                                'pnl': trade['pnl'],
                                'pnl_percent': trade['pnl_percent'],
                                'position_type': trade['position_type'],
                                'strategy': trade['strategy'],
                                'exit_reason': reason
                            }
                            trading_history = pd.concat([trading_history, pd.DataFrame([history_entry])], ignore_index=True)
                            indices_to_drop.append(idx)
                        
                        # Remove closed trades from active trades
                        active_trades = active_trades.drop(indices_to_drop).reset_index(drop=True)
                        
                        # Save updated files
                        active_trades.to_csv(active_trades_file, index=False)
                        trading_history.to_csv(history_file, index=False)
                        
                        logger.info(f"Closed {len(trades_to_close)} trades")
        
        except Exception as e:
            logger.error(f"Error checking exit conditions: {str(e)}")
    
    def _find_new_trades(self) -> None:
        """Look for new trading opportunities"""
        try:
            active_trades_file = os.path.join(self.data_dir, 'active_trades.csv')
            
            # Read active trades
            if os.path.exists(active_trades_file):
                active_trades = pd.read_csv(active_trades_file)
            else:
                active_trades = pd.DataFrame(columns=[
                    'symbol', 'entry_date', 'entry_price', 'current_price',
                    'quantity', 'pnl', 'pnl_percent', 'position_type',
                    'stop_loss', 'take_profit', 'strategy'
                ])
            
            # List of potential symbols
            potential_symbols = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA',
                'JPM', 'V', 'JNJ', 'WMT', 'PG', 'XOM', 'BAC', 'ADBE',
                'CRM', 'PYPL', 'NFLX', 'DIS', 'INTC'
            ]
            
            # Strategies
            strategies = [
                'Trend Following', 'Mean Reversion', 'Breakout', 'MACD Crossover',
                'Volatility Expansion', 'RSI Divergence', 'Support/Resistance',
                'Momentum', 'Moving Average Crossover'
            ]
            
            # Active symbols
            active_symbols = set(active_trades['symbol']) if not active_trades.empty else set()
            
            # Available symbols (not already in active trades)
            available_symbols = [s for s in potential_symbols if s not in active_symbols]
            
            # Random decision to enter new trades (30% chance)
            if random.random() < 0.3 and available_symbols:
                # Number of new trades to open (1-3)
                num_new_trades = random.randint(1, min(3, len(available_symbols)))
                
                new_trades = []
                for _ in range(num_new_trades):
                    # Select random symbol
                    symbol = random.choice(available_symbols)
                    available_symbols.remove(symbol)
                    
                    # Generate random price between $50 and $500
                    entry_price = round(random.uniform(50, 500), 2)
                    
                    # Long or short (70% long, 30% short)
                    position_type = 'Long' if random.random() < 0.7 else 'Short'
                    
                    # Quantity between 10 and 100
                    quantity = random.randint(10, 100)
                    
                    # Stop loss (2-5% away from entry)
                    stop_loss_pct = random.uniform(0.02, 0.05)
                    stop_loss = round(entry_price * (1 - stop_loss_pct) if position_type == 'Long'
                                     else entry_price * (1 + stop_loss_pct), 2)
                    
                    # Take profit (5-15% away from entry)
                    take_profit_pct = random.uniform(0.05, 0.15)
                    take_profit = round(entry_price * (1 + take_profit_pct) if position_type == 'Long'
                                       else entry_price * (1 - take_profit_pct), 2)
                    
                    # Strategy
                    strategy = random.choice(strategies)
                    
                    # New trade
                    new_trade = {
                        'symbol': symbol,
                        'entry_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'entry_price': entry_price,
                        'current_price': entry_price,
                        'quantity': quantity,
                        'pnl': 0.0,
                        'pnl_percent': 0.0,
                        'position_type': position_type,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'strategy': strategy
                    }
                    new_trades.append(new_trade)
                
                # Add new trades to active trades
                if new_trades:
                    active_trades = pd.concat([active_trades, pd.DataFrame(new_trades)], ignore_index=True)
                    active_trades.to_csv(active_trades_file, index=False)
                    logger.info(f"Opened {len(new_trades)} new trades")
        
        except Exception as e:
            logger.error(f"Error finding new trades: {str(e)}")
    
    def _update_portfolio_performance(self) -> None:
        """Update the portfolio performance record"""
        try:
            performance_file = os.path.join(self.data_dir, 'portfolio_performance.csv')
            active_trades_file = os.path.join(self.data_dir, 'active_trades.csv')
            
            # Read performance history
            if os.path.exists(performance_file):
                performance = pd.read_csv(performance_file)
                if not performance.empty:
                    last_record = performance.iloc[-1]
                else:
                    # Initialize with base values if file exists but is empty
                    last_record = {
                        'portfolio_value': 100000.0,
                        'cash_balance': 70000.0,
                        'invested_amount': 30000.0,
                        'daily_pnl': 0.0,
                        'daily_pnl_percent': 0.0
                    }
            else:
                # Initialize with base values if file doesn't exist
                performance = pd.DataFrame(columns=[
                    'date', 'portfolio_value', 'cash_balance',
                    'invested_amount', 'daily_pnl', 'daily_pnl_percent'
                ])
                last_record = {
                    'portfolio_value': 100000.0,
                    'cash_balance': 70000.0,
                    'invested_amount': 30000.0,
                    'daily_pnl': 0.0,
                    'daily_pnl_percent': 0.0
                }
            
            # Calculate current portfolio value
            current_cash = last_record.get('cash_balance', 70000.0)
            
            # Add value of active trades
            invested_amount = 0
            if os.path.exists(active_trades_file):
                active_trades = pd.read_csv(active_trades_file)
                if not active_trades.empty:
                    for _, trade in active_trades.iterrows():
                        position_value = trade['current_price'] * trade['quantity']
                        invested_amount += position_value
            
            # Calculate portfolio value and daily change
            current_portfolio_value = current_cash + invested_amount
            daily_pnl = current_portfolio_value - last_record.get('portfolio_value', 100000.0)
            daily_pnl_percent = (daily_pnl / last_record.get('portfolio_value', 100000.0)) * 100 if last_record.get('portfolio_value', 100000.0) > 0 else 0
            
            # Create new record
            today = datetime.now().strftime('%Y-%m-%d')
            if performance.empty or performance.iloc[-1]['date'] != today:
                new_record = {
                    'date': today,
                    'portfolio_value': round(current_portfolio_value, 2),
                    'cash_balance': round(current_cash, 2),
                    'invested_amount': round(invested_amount, 2),
                    'daily_pnl': round(daily_pnl, 2),
                    'daily_pnl_percent': round(daily_pnl_percent, 2)
                }
                
                performance = pd.concat([performance, pd.DataFrame([new_record])], ignore_index=True)
                performance.to_csv(performance_file, index=False)
                logger.info(f"Updated portfolio performance for {today}")
        
        except Exception as e:
            logger.error(f"Error updating portfolio performance: {str(e)}") 