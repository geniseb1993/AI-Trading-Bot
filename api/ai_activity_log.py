"""
AI Activity Log Module

This module provides functionality to log AI trading bot activities,
including trade decisions, system actions, and errors.
"""

import logging
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class ActivityType(str, Enum):
    """Types of AI activities that can be logged"""
    TRADE_ENTRY = "trade_entry"
    TRADE_EXIT = "trade_exit"
    SIGNAL_GENERATED = "signal_generated"
    STRATEGY_SWITCH = "strategy_switch"
    MARKET_ANALYSIS = "market_analysis"
    RISK_ADJUSTMENT = "risk_adjustment"
    SYSTEM_ACTION = "system_action"
    ERROR = "error"
    BACKTEST = "backtest"
    OTHER = "other"

class AIActivityLogger:
    """
    Class to log and retrieve AI trading bot activities
    """
    
    def __init__(self, log_file_path: str = "data/ai_activity_log.json"):
        """
        Initialize the AI Activity Logger
        
        Args:
            log_file_path: Path to the JSON log file
        """
        self.log_file_path = log_file_path
        self.logs = self._load_logs()
        self._ensure_directory_exists()
        
    def _ensure_directory_exists(self):
        """Ensure the directory for the log file exists"""
        directory = os.path.dirname(self.log_file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def _load_logs(self) -> List[Dict[str, Any]]:
        """Load existing logs from file"""
        try:
            if os.path.exists(self.log_file_path):
                with open(self.log_file_path, 'r') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            logger.error(f"Error loading activity logs: {e}")
            return []
    
    def _save_logs(self):
        """Save logs to file"""
        try:
            with open(self.log_file_path, 'w') as f:
                json.dump(self.logs, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving activity logs: {e}")
    
    def log_activity(
        self,
        activity_type: ActivityType,
        description: str,
        details: Dict[str, Any] = None,
        symbol: str = None,
        source: str = "ai_trader"
    ) -> Dict[str, Any]:
        """
        Log an AI activity
        
        Args:
            activity_type: Type of activity
            description: Short description of the activity
            details: Additional details as a dictionary
            symbol: Trading symbol related to the activity (if applicable)
            source: Source of the activity (default: ai_trader)
            
        Returns:
            The created log entry
        """
        timestamp = datetime.now().isoformat()
        log_entry = {
            "id": f"{int(time.time() * 1000)}_{hash(description) & 0xFFFFFFFF}",
            "timestamp": timestamp,
            "activity_type": activity_type,
            "description": description,
            "details": details or {},
            "symbol": symbol,
            "source": source
        }
        
        self.logs.append(log_entry)
        self._save_logs()
        logger.info(f"Activity logged: [{activity_type}] {description}")
        
        return log_entry
    
    def get_logs(
        self,
        limit: int = 100,
        activity_type: Optional[ActivityType] = None,
        symbol: Optional[str] = None,
        source: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get filtered activity logs
        
        Args:
            limit: Maximum number of logs to return
            activity_type: Filter by activity type
            symbol: Filter by trading symbol
            source: Filter by source
            start_time: Filter logs after this ISO timestamp
            end_time: Filter logs before this ISO timestamp
            
        Returns:
            List of filtered log entries
        """
        filtered_logs = self.logs.copy()
        
        # Apply filters
        if activity_type:
            filtered_logs = [log for log in filtered_logs 
                             if log.get("activity_type") == activity_type]
        
        if symbol:
            filtered_logs = [log for log in filtered_logs 
                             if log.get("symbol") == symbol]
        
        if source:
            filtered_logs = [log for log in filtered_logs 
                             if log.get("source") == source]
        
        if start_time:
            filtered_logs = [log for log in filtered_logs 
                             if log.get("timestamp", "") >= start_time]
        
        if end_time:
            filtered_logs = [log for log in filtered_logs 
                             if log.get("timestamp", "") <= end_time]
        
        # Sort by timestamp (newest first)
        filtered_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Apply limit
        return filtered_logs[:limit]
    
    def clear_logs(self):
        """Clear all logs"""
        self.logs = []
        self._save_logs()
        logger.info("All activity logs cleared")

# Create a singleton instance
_activity_logger_instance = None

def get_activity_logger() -> AIActivityLogger:
    """Get or create the singleton activity logger instance"""
    global _activity_logger_instance
    if _activity_logger_instance is None:
        _activity_logger_instance = AIActivityLogger()
    return _activity_logger_instance 