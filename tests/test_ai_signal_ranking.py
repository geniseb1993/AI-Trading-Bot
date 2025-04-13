"""
Unit tests for AISignalRanking
"""
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import json
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from execution_model.ai_signal_ranking import AISignalRanking

class TestAISignalRanking(unittest.TestCase):
    """Test the AISignalRanking class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "ai_signal_ranking": {
                "volume_weight": 0.25,
                "trend_weight": 0.25,
                "historical_weight": 0.3,
                "institutional_weight": 0.2,
            }
        }
        
        # Create mock PnL logger
        self.mock_pnl_logger = MagicMock()
        self.mock_pnl_logger.get_trade_history.return_value = pd.DataFrame({
            'symbol': ['AAPL', 'MSFT', 'AAPL', 'MSFT', 'GOOG'],
            'strategy_name': ['Breakout', 'Support', 'Breakout', 'Resistance', 'Trend'],
            'pnl': [100, -50, 200, 75, -25]
        })
        
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {'OPENROUTER_API_KEY': 'fake_key'})
        self.env_patcher.start()
        
        # Mock OpenAI client
        self.openai_patcher = patch('execution_model.ai_signal_ranking.OpenAI')
        self.mock_openai = self.openai_patcher.start()
        self.mock_client = MagicMock()
        self.mock_openai.return_value = self.mock_client
        
        # Create sample market data
        self.market_data = {
            'AAPL': pd.DataFrame({
                'close': [150, 152, 153, 155, 154],
                'volume': [1000000, 1200000, 950000, 1500000, 1100000],
                'high': [153, 154, 155, 157, 156],
                'low': [148, 150, 151, 153, 152]
            }),
            'MSFT': pd.DataFrame({
                'close': [250, 255, 253, 260, 258],
                'volume': [2000000, 1900000, 2100000, 2500000, 2200000],
                'high': [253, 258, 255, 262, 260],
                'low': [248, 252, 250, 257, 255]
            })
        }
        
        # Initialize the AISignalRanking instance
        self.ranker = AISignalRanking(self.config, self.mock_pnl_logger)
    
    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
        self.openai_patcher.stop()
    
    def test_initialization(self):
        """Test initialization of AISignalRanking"""
        self.assertEqual(self.ranker.feature_weights['volume_ratio'], 0.25)
        self.assertEqual(self.ranker.feature_weights['trend_strength'], 0.25)
        self.assertEqual(self.ranker.feature_weights['historical_win_rate'], 0.3)
        self.assertEqual(self.ranker.feature_weights['institutional_flow'], 0.2)
        
        # Test historical performance loading
        self.assertIn('AAPL', self.ranker.historical_performance)
        self.assertIn('Breakout', self.ranker.historical_performance)
    
    def test_rank_signals(self):
        """Test signal ranking functionality"""
        signals = [
            {'symbol': 'AAPL', 'setup_type': 'Breakout', 'direction': 'BUY'},
            {'symbol': 'MSFT', 'setup_type': 'Support', 'direction': 'BUY'}
        ]
        
        ranked_signals = self.ranker.rank_signals(signals, self.market_data)
        
        # Check that we have the same number of signals
        self.assertEqual(len(ranked_signals), len(signals))
        
        # Check that each signal has an AI confidence score
        for signal in ranked_signals:
            self.assertIn('ai_confidence', signal)
            self.assertIn('ranking_factors', signal)
            
        # First signal should have higher confidence
        self.assertGreaterEqual(ranked_signals[0]['ai_confidence'], ranked_signals[1]['ai_confidence'])
    
    def test_rank_signals_with_missing_market_data(self):
        """Test signal ranking with missing market data"""
        signals = [
            {'symbol': 'AAPL', 'setup_type': 'Breakout', 'direction': 'BUY'},
            {'symbol': 'GOOG', 'setup_type': 'Support', 'direction': 'BUY'}  # No market data for GOOG
        ]
        
        ranked_signals = self.ranker.rank_signals(signals, self.market_data)
        
        # Check that we have the same number of signals
        self.assertEqual(len(ranked_signals), len(signals))
        
        # The GOOG signal should have default confidence
        goog_signal = next(s for s in ranked_signals if s['symbol'] == 'GOOG')
        self.assertEqual(goog_signal['ai_confidence'], 0.5)
    
    @patch('execution_model.ai_signal_ranking.AISignalRanking._create_market_analysis_prompt')
    def test_get_gpt_insights(self, mock_create_prompt):
        """Test GPT insights generation"""
        # Mock prompt creation
        mock_create_prompt.return_value = "Test prompt"
        
        # Mock GPT response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """
        Market Summary: Markets are showing moderate strength with mixed signals.
        
        Key Market Trends:
        1. Technology sector is outperforming other sectors
        2. Increased volatility in small-cap stocks
        
        Trading Opportunities:
        AAPL: BUY
        Entry strategy: Buy on pullback to support level
        Stop Loss: 150
        Target: 170
        Rationale: Strong earnings and positive momentum
        
        MSFT: SELL
        Entry strategy: Sell on break of support
        Stop Loss: 265
        Target: 245
        Rationale: Weakening technical indicators
        """
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Test with available symbols
        insights = self.ranker.get_gpt_insights(['AAPL', 'MSFT'], self.market_data)
        
        # Verify result structure
        self.assertIn('market_summary', insights)
        self.assertIn('key_trends', insights)
        self.assertIn('trade_opportunities', insights)
        
        # Verify content
        self.assertGreater(len(insights['market_summary']), 0)
        self.assertEqual(len(insights['key_trends']), 2)
        self.assertEqual(len(insights['trade_opportunities']), 2)
        
        # Verify that GPT was called correctly
        self.mock_client.chat.completions.create.assert_called_once()
    
    def test_parse_gpt_insights(self):
        """Test parsing GPT response into structured insights"""
        gpt_response = """
        Market Summary: Markets are trending upward with strong volume.
        
        Key Market Trends:
        1. Technology sector outperforming
        2. Energy sector weakness
        
        Trading Opportunities:
        AAPL: BUY
        Entry strategy: Buy on breakout above $155
        Stop Loss: 150
        Target: 165
        Rationale: Strong technical setup and earnings momentum
        
        MSFT: SELL
        Entry strategy: Sell on break below $255
        Stop Loss: 260
        Target: 245
        Rationale: Bearish divergence and weakening momentum
        """
        
        parsed = self.ranker._parse_gpt_insights(gpt_response)
        
        # Verify market summary
        self.assertIn("trending upward", parsed['market_summary'].lower())
        
        # Verify key trends
        self.assertEqual(len(parsed['key_trends']), 2)
        self.assertIn("Technology", parsed['key_trends'][0])
        
        # Verify trading opportunities
        self.assertEqual(len(parsed['trade_opportunities']), 2)
        
        # Check AAPL opportunity
        aapl_opp = next(o for o in parsed['trade_opportunities'] if o['symbol'] == 'AAPL')
        self.assertEqual(aapl_opp['direction'], 'BUY')
        self.assertEqual(aapl_opp['stop_loss'], 150)
        self.assertEqual(aapl_opp['target'], 165)
        self.assertIn("technical setup", aapl_opp['rationale'])
        
        # Check MSFT opportunity
        msft_opp = next(o for o in parsed['trade_opportunities'] if o['symbol'] == 'MSFT')
        self.assertEqual(msft_opp['direction'], 'SELL')
        self.assertEqual(msft_opp['stop_loss'], 260)
        self.assertEqual(msft_opp['target'], 245)
    
    def test_create_market_analysis_prompt(self):
        """Test creation of market analysis prompt"""
        prompt_data = {
            'AAPL': 'Price: 155, RSI: 65, Volume: +20% over average',
            'MSFT': 'Price: 258, RSI: 45, Volume: -5% below average'
        }
        
        recent_signals = [
            {'symbol': 'AAPL', 'direction': 'BUY', 'setup_type': 'Breakout', 'ai_confidence': 0.85},
            {'symbol': 'MSFT', 'direction': 'SELL', 'setup_type': 'Resistance', 'ai_confidence': 0.75},
        ]
        
        prompt = self.ranker._create_market_analysis_prompt(prompt_data, recent_signals)
        
        # Verify prompt structure
        self.assertIn('You are a professional market analyst', prompt)
        self.assertIn('AAPL Market Data', prompt)
        self.assertIn('MSFT Market Data', prompt)
        self.assertIn('Recent Trading Signals', prompt)
        self.assertIn('AAPL: BUY signal', prompt)
        self.assertIn('MSFT: SELL signal', prompt)
        
        # Verify response requirements
        self.assertIn('Market Summary', prompt)
        self.assertIn('Key Market Trends', prompt)
        self.assertIn('Trading Opportunities', prompt)

if __name__ == '__main__':
    unittest.main() 