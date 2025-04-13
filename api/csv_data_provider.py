import os
import pandas as pd
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CSVDataProvider:
    """Provides data from CSV files located in the data directory"""
    
    def __init__(self, data_dir=None):
        """Initialize with path to data directory"""
        # Handle relative and absolute paths
        if data_dir is None:
            # Get the path to the project root directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            self.data_dir = os.path.join(project_root, "data")
        else:
            self.data_dir = data_dir
        
        logger.info(f"CSV Data Provider initialized with data directory: {self.data_dir}")
        self.verify_data_files()
        
    def verify_data_files(self):
        """Verify that required data files exist"""
        required_files = [
            "portfolio_performance.csv",
            "market_overview.csv",
            "active_trades.csv",
            "trading_history.csv",
            "strategy_performance.csv",
            "risk_metrics.csv"
        ]
        
        missing_files = []
        for file in required_files:
            file_path = os.path.join(self.data_dir, file)
            if not os.path.exists(file_path):
                logger.warning(f"Data file not found: {file_path}")
                missing_files.append(file)
            else:
                logger.info(f"Data file found: {file_path}")
        
        if missing_files:
            logger.warning(f"The following data files are missing: {', '.join(missing_files)}")
            logger.warning(f"Check that the data directory exists at: {self.data_dir}")
        else:
            logger.info(f"All required data files found in {self.data_dir}")
    
    def _read_csv(self, filename):
        """Read a CSV file and return as a DataFrame"""
        try:
            file_path = os.path.join(self.data_dir, filename)
            logger.info(f"Reading CSV file: {file_path}")
            return pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Error reading {filename}: {str(e)}")
            return pd.DataFrame()
    
    def get_portfolio_performance(self):
        """Get portfolio performance data"""
        df = self._read_csv("portfolio_performance.csv")
        if df.empty:
            return []
        return df.to_dict('records')
    
    def get_market_overview(self):
        """Get market overview data"""
        df = self._read_csv("market_overview.csv")
        if df.empty:
            return []
        
        # Extract market indices
        main_df = df[df['symbol'].notna()]
        
        # Check if there's an index_name column for separate indices data
        indices_df = None
        if 'index_name' in df.columns:
            indices_df = df[df['index_name'].notna()]
        
        # Check if there's a sector column for sector performance
        sector_df = None
        if 'sector' in df.columns and any(df['sector'].notna()):
            sector_df = df[df['sector'].notna() & df['price'].isna()]
        
        result = {
            'market_data': main_df.to_dict('records'),
            'indices': indices_df.to_dict('records') if indices_df is not None else [],
            'sectors': sector_df.to_dict('records') if sector_df is not None else []
        }
        
        return result
    
    def get_active_trades(self):
        """Get active trades data"""
        df = self._read_csv("active_trades.csv")
        if df.empty:
            return []
        return df.to_dict('records')
    
    def get_trading_history(self):
        """Get trading history data"""
        df = self._read_csv("trading_history.csv")
        if df.empty:
            return []
        return df.to_dict('records')
    
    def get_strategy_performance(self):
        """Get strategy performance data"""
        df = self._read_csv("strategy_performance.csv")
        if df.empty:
            return []
        return df.to_dict('records')
    
    def get_risk_metrics(self):
        """Get risk metrics data"""
        df = self._read_csv("risk_metrics.csv")
        if df.empty:
            return []
        return df.to_dict('records')
    
    def get_dashboard_data(self):
        """Get all data needed for the dashboard"""
        return {
            'portfolio_performance': self.get_portfolio_performance(),
            'market_overview': self.get_market_overview(),
            'active_trades': self.get_active_trades(),
            'trading_history': self.get_trading_history(),
            'strategy_performance': self.get_strategy_performance(),
            'risk_metrics': self.get_risk_metrics(),
            'timestamp': datetime.now().isoformat()
        } 