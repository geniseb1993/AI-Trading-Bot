import React, { useEffect, useState } from 'react';
import axios from 'axios';

const InstitutionalFlow = () => {
  const [symbols, setSymbols] = useState([]);
  const [loading, setLoading] = useState(false);
  const [flowData, setFlowData] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    if (symbols.length > 0) {
      setLoading(true);
      analyzeFlow();
    }
  }, [symbols]); // eslint-disable-line react-hooks/exhaustive-deps

  const analyzeFlow = async () => {
    try {
      const response = await axios.post('/api/execution-model/analyze/flow', {
        symbols,
        days_back: 7
      });
      
      if (response.data && response.data.flow_analysis) {
        setFlowData(response.data.flow_analysis);
        setError(null);
      } else {
        throw new Error('Invalid flow data received');
      }
    } catch (err) {
      console.error(err);
      setError('Failed to fetch institutional flow data');
      
      // Generate fallback mock data when API is unavailable
      const mockFlowData = {};
      for (const symbol of symbols) {
        const optionsSignal = Math.random() * 2 - 1; // Between -1 and 1
        const darkPoolSignal = Math.random() * 2 - 1; // Between -1 and 1
        const signal = (optionsSignal * 0.6 + darkPoolSignal * 0.4).toFixed(2);
        const confidence = (0.5 + Math.random() * 0.45).toFixed(2);
        
        mockFlowData[symbol] = {
          symbol: symbol,
          options_signal: optionsSignal.toFixed(2),
          dark_pool_signal: darkPoolSignal.toFixed(2),
          signal: signal,
          confidence: confidence,
          has_significant_flow: Math.abs(signal) > 0.4,
          details: `Mock institutional flow data for ${symbol}. API server might be down.`,
          days_analyzed: 7
        };
      }
      
      setFlowData(mockFlowData);
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

export default InstitutionalFlow; 