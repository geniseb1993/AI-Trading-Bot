import React, { useEffect, useState } from 'react';
import axios from 'axios';

const MarketAnalysis = () => {
  const [symbols, setSymbols] = useState([]);
  const [marketData, setMarketData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (symbols.length > 0) {
      setLoading(true);
      analyzeMarket();
    }
  }, [symbols]); // eslint-disable-line react-hooks/exhaustive-deps

  const analyzeMarket = async () => {
    try {
      const response = await axios.post('/api/execution-model/analyze/market', {
        symbols,
        timeframe: '1d',
        limit: 100
      });
      
      if (response.data && response.data.analysis) {
        setMarketData(response.data.analysis);
        setError(null);
      } else {
        throw new Error('Invalid market data received');
      }
    } catch (err) {
      console.error(err);
      setError('Failed to fetch market analysis data');
      
      // Generate fallback mock data when API is unavailable
      const mockMarketData = {};
      for (const symbol of symbols) {
        // Generate random values
        const trendDirection = Math.random() > 0.5 ? 0.5 : -0.5;
        
        mockMarketData[symbol] = {
          symbol: symbol,
          trend: {
            direction: trendDirection,
            strength: Math.random()
          },
          volatility: {
            atr: Math.random() * 3 + 1,
            historical_volatility: Math.random() * 0.05
          },
          momentum: {
            rsi: 30 + Math.random() * 40,
            macd: Math.random() * 2 - 1
          },
          volume: {
            profile: 0.8 + Math.random() * 0.7
          },
          support_resistance: {
            support_levels: [
              Math.floor(Math.random() * 100 + 50),
              Math.floor(Math.random() * 100 + 40)
            ],
            resistance_levels: [
              Math.floor(Math.random() * 100 + 60),
              Math.floor(Math.random() * 100 + 70)
            ]
          },
          market_regime: ['trending_up', 'trending_down', 'volatile', 'ranging', 'calm'][Math.floor(Math.random() * 5)],
          details: `Mock market analysis data for ${symbol}. API server might be down.`
        };
      }
      
      setMarketData(mockMarketData);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Render your component content here */}
    </div>
  );
};

export default MarketAnalysis; 