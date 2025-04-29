import React, { useEffect, useState, useCallback } from 'react';
import { useInstitutionalFlowData } from '../contexts/DataContext';
import { institutionalFlowService } from '../services/api';

const InstitutionalFlow = () => {
  // Use the domain-specific hook from our DataContext
  const { 
    data: flowData, 
    loading, 
    error,
    updateData: setFlowData,
    setLoading,
    setError
  } = useInstitutionalFlowData();
  
  // Local component state
  const [symbols, setSymbols] = useState([]);
  const [dataSource, setDataSource] = useState('');
  const [smartMoneyMoves, setSmartMoneyMoves] = useState([]);

  useEffect(() => {
    if (symbols.length > 0) {
      analyzeFlow();
    }
  }, [symbols]); // eslint-disable-line react-hooks/exhaustive-deps

  const analyzeFlow = useCallback(async () => {
    try {
      setLoading(true);
      
      // Use our service to fetch data
      const response = await institutionalFlowService.getEnhancedAnalysis({
        symbols,
        days_back: 7
      });
      
      if (response && response.flow_analysis) {
        // Update global state with our domain-specific method
        setFlowData(response.flow_analysis);
        
        // These remain in component state since they're component-specific
        setDataSource(response.source || 'Unknown');
        setSmartMoneyMoves(response.smart_money_moves || []);
      } else {
        throw new Error('Invalid flow data received');
      }
    } catch (err) {
      console.error('Error analyzing flow:', err);
      setError(err.message || 'Failed to analyze institutional flow');
    }
  }, [symbols, setFlowData, setLoading, setError]);

  const addSymbol = (symbol) => {
    if (symbol && !symbols.includes(symbol)) {
      setSymbols([...symbols, symbol]);
    }
  };

  const removeSymbol = (symbol) => {
    setSymbols(symbols.filter(s => s !== symbol));
  };

  // Function to determine signal color based on value
  const getSignalColor = (signal) => {
    const value = parseFloat(signal);
    if (value > 0.5) return 'green';
    if (value > 0.1) return 'lightgreen';
    if (value < -0.5) return 'red';
    if (value < -0.1) return 'lightcoral';
    return 'gray';
  };

  return (
    <div className="institutional-flow-container">
      {loading ? (
        <div className="loading">Loading institutional flow data...</div>
      ) : error ? (
        <div className="error-container">
          <div className="error-message">{error}</div>
          <button onClick={analyzeFlow} className="retry-button">
            Retry
          </button>
        </div>
      ) : (
        <div className="flow-content">
          <div className="data-source">
            Data Source: {dataSource}
          </div>
          
          {/* Display flow analysis data */}
          {Object.keys(flowData).length > 0 && (
            <div className="flow-analysis-table">
              <h3>Institutional Flow Analysis</h3>
              <table>
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Signal</th>
                    <th>Options</th>
                    <th>Dark Pool</th>
                    <th>Confidence</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(flowData).map(([symbol, data]) => (
                    <tr key={symbol}>
                      <td>{symbol}</td>
                      <td style={{ color: getSignalColor(data.signal) }}>
                        {data.signal}
                      </td>
                      <td>{data.options_signal}</td>
                      <td>{data.dark_pool_signal}</td>
                      <td>{data.confidence}</td>
                      <td>{data.details}</td>
                      <td>
                        <button onClick={() => removeSymbol(symbol)}>Remove</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          
          {/* Display smart money moves if available */}
          {smartMoneyMoves.length > 0 && (
            <div className="smart-money-moves">
              <h3>Smart Money Moves</h3>
              <ul>
                {smartMoneyMoves.map((move, index) => (
                  <li key={index} className={move.direction}>
                    <strong>{move.symbol}</strong>: {move.description} by {move.institution}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      
      <div>
        <input
          type="text"
          placeholder="Add symbol (e.g., AAPL)"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && e.target.value) {
              addSymbol(e.target.value.toUpperCase());
              e.target.value = '';
            }
          }}
        />
        <button onClick={analyzeFlow}>Refresh Analysis</button>
      </div>
    </div>
  );
};

export default InstitutionalFlow; 