import logging
import time
import threading
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import queue

from .trade_executor import TradeExecutor
from .broker_manager import BrokerManager

logger = logging.getLogger(__name__)

class AutoTrader:
    """
    Automated trading system that monitors for signals and executes trades
    based on configurable parameters and risk management rules.
    """
    
    def __init__(
        self, 
        broker_manager: BrokerManager,
        config_file: str = "broker_config.json"
    ):
        """
        Initialize the AutoTrader
        
        Args:
            broker_manager: BrokerManager instance for interacting with brokers
            config_file: Path to config file
        """
        self.broker_manager = broker_manager
        self.trade_executor = TradeExecutor(broker_manager)
        self.config_file = config_file
        self.config = self._load_config()
        
        # Queue for trade signals
        self.signal_queue = queue.Queue()
        
        # Active monitoring thread
        self.monitoring_thread = None
        self.running = False
        
        # Trade history
        self.trade_history = []
        
        logger.info("AutoTrader initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults."""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
                return config
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load config file, using defaults: {e}")
            # Default configuration
            return {
                "enabled": False,
                "risk_per_trade": 0.01,  # 1% of account per trade
                "max_open_trades": 5,
                "max_position_size": 0.20,  # Max 20% of account in one position
                "ignored_symbols": [],
                "broker_preferences": {
                    "alpaca": True,
                    "mock": True
                }
            }
    
    def _save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
                logger.info(f"Saved configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def start(self):
        """Start the auto-trading system."""
        if self.running:
            logger.warning("AutoTrader is already running")
            return False
        
        self.running = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info("AutoTrader started")
        return True
    
    def stop(self):
        """Stop the auto-trading system."""
        if not self.running:
            logger.warning("AutoTrader is not running")
            return False
        
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("AutoTrader stopped")
        return True
    
    def add_signal(self, signal: Dict[str, Any]):
        """
        Add a trading signal to the processing queue
        
        Args:
            signal: Dict containing signal information
                Required keys: 
                    - symbol: Trading symbol
                    - position_type: "LONG" or "SHORT"
                    - entry_price: Target entry price
                Optional keys:
                    - stop_loss: Stop loss price
                    - take_profit: Take profit price
                    - quantity: Number of shares/contracts
                    - signal_score: Score indicating signal strength (0-10)
        """
        # Validate required fields
        required_fields = ["symbol", "position_type", "entry_price"]
        for field in required_fields:
            if field not in signal:
                logger.error(f"Signal missing required field: {field}")
                return False
        
        # Add timestamp if not present
        if "timestamp" not in signal:
            signal["timestamp"] = datetime.now().isoformat()
        
        # Put in processing queue
        self.signal_queue.put(signal)
        logger.info(f"Added signal for {signal['symbol']} to queue")
        return True
    
    def _monitoring_loop(self):
        """Main monitoring loop that processes signals."""
        while self.running:
            try:
                # Check if auto trading is enabled
                if not self.config.get("enabled", False):
                    time.sleep(5)
                    continue
                
                # Get active broker
                active_broker = self.broker_manager.get_broker()
                
                # Process signals in queue
                while not self.signal_queue.empty():
                    signal = self.signal_queue.get()
                    
                    # Check if symbol is in ignored list
                    if signal["symbol"] in self.config.get("ignored_symbols", []):
                        logger.info(f"Ignoring signal for {signal['symbol']} (in ignored list)")
                        continue
                    
                    # Get account info
                    account_info = self.trade_executor.get_account_info()
                    
                    if not account_info.get("success"):
                        logger.error(f"Failed to get account info: {account_info.get('error')}")
                        continue
                    
                    account = account_info.get("account", {})
                    
                    # Count open trades to check against limit
                    positions = self.trade_executor.get_positions()
                    if positions.get("success"):
                        open_trades = len(positions.get("positions", []))
                        if open_trades >= self.config.get("max_open_trades", 5):
                            logger.warning(f"Max open trades limit reached ({open_trades})")
                            continue
                    
                    # Process the signal
                    self._process_signal(signal, account)
                
                # Sleep to prevent excessive CPU usage
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def _process_signal(self, signal: Dict[str, Any], account: Dict[str, Any]):
        """
        Process a trade signal and execute if criteria are met
        
        Args:
            signal: The trade signal dictionary
            account: Account information
        """
        try:
            symbol = signal["symbol"]
            position_type = signal["position_type"]
            entry_price = signal["entry_price"]
            
            # Determine if we should use market or limit order
            use_market = signal.get("use_market", False)
            
            # Calculate position size if not provided
            quantity = signal.get("quantity")
            if not quantity:
                quantity = self._calculate_position_size(signal, account)
            
            if quantity <= 0:
                logger.warning(f"Calculated position size too small for {symbol}, skipping")
                return
            
            # Ensure we have stop loss for risk management
            stop_loss = signal.get("stop_loss")
            if not stop_loss:
                logger.error(f"No stop loss provided for {symbol} signal")
                return
            
            # Optional take profit
            take_profit = signal.get("take_profit")
            
            # Execute the trade
            side = "buy" if position_type == "LONG" else "sell"
            trade_result = self.trade_executor.execute_trade_with_risk_management(
                symbol=symbol,
                qty=quantity,
                side=side,
                entry_price=None if use_market else entry_price,
                stop_loss_price=stop_loss,
                take_profit_price=take_profit,
                use_market_order=use_market
            )
            
            if trade_result.get("success"):
                # Log successful trade execution
                trade_record = {
                    "timestamp": datetime.now().isoformat(),
                    "symbol": symbol,
                    "side": side,
                    "quantity": quantity,
                    "entry_order": trade_result.get("entry_order"),
                    "stop_loss_order": trade_result.get("stop_loss_order"),
                    "take_profit_order": trade_result.get("take_profit_order"),
                    "signal": signal
                }
                self.trade_history.append(trade_record)
                logger.info(f"Successfully executed {side} order for {quantity} {symbol}")
            else:
                logger.error(f"Failed to execute trade for {symbol}: {trade_result.get('error')}")
        
        except Exception as e:
            logger.error(f"Error processing signal for {signal.get('symbol')}: {e}")
    
    def _calculate_position_size(self, signal: Dict[str, Any], account: Dict[str, Any]) -> int:
        """
        Calculate appropriate position size based on account value and risk parameters
        
        Args:
            signal: The trade signal dictionary
            account: Account information dictionary
        
        Returns:
            int: Number of shares to trade
        """
        try:
            # Get account equity
            equity = account.get("equity", 0)
            if equity <= 0:
                logger.error("Invalid account equity")
                return 0
            
            # Risk amount (% of portfolio)
            risk_per_trade = self.config.get("risk_per_trade", 0.01)
            risk_amount = equity * risk_per_trade
            
            # Calculate risk per share
            entry_price = signal.get("entry_price", 0)
            stop_loss = signal.get("stop_loss", 0)
            
            if not entry_price or not stop_loss:
                logger.error("Missing entry price or stop loss price")
                return 0
            
            # Calculate risk per share
            risk_per_share = abs(entry_price - stop_loss)
            
            if risk_per_share <= 0:
                logger.error("Invalid risk per share (zero or negative)")
                return 0
            
            # Calculate position size based on risk
            shares = int(risk_amount / risk_per_share)
            
            # Check against max position size
            max_position_size = self.config.get("max_position_size", 0.20)
            max_shares = int((equity * max_position_size) / entry_price)
            shares = min(shares, max_shares)
            
            # Check against available buying power
            cash = account.get("cash", 0)
            required_cash = shares * entry_price
            if required_cash > cash:
                shares = int(cash / entry_price)
            
            return max(1, shares)  # Ensure at least 1 share
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the auto-trader
        
        Returns:
            dict: Status information
        """
        return {
            "running": self.running,
            "enabled": self.config.get("enabled", False),
            "signals_in_queue": self.signal_queue.qsize(),
            "config": self.config,
            "trade_history_count": len(self.trade_history)
        }
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Update auto-trader configuration
        
        Args:
            new_config: Dictionary with new configuration values
        
        Returns:
            bool: Success status
        """
        try:
            self.config.update(new_config)
            self._save_config()
            return True
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_trade_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent trade history
        
        Args:
            limit: Maximum number of trades to return
        
        Returns:
            list: List of trade records
        """
        return self.trade_history[-limit:] if self.trade_history else [] 