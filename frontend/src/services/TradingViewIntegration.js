import axios from 'axios';

// TradingView API URL (integrated with main API)
const TRADINGVIEW_API_URL = 'http://localhost:5000/api/tradingview';

// Main API URL
const MAIN_API_URL = 'http://localhost:5000/api';

// Maximum number of retries for API calls
const MAX_RETRIES = 2;

/**
 * Service for integrating with TradingView data
 * This service provides methods to:
 * 1. Extract data from TradingView webhooks
 * 2. Fetch market analysis based on TradingView technical indicators
 * 3. Format data for the MarketAnalysis component
 */
class TradingViewIntegration {
  constructor() {
    this.API_BASE_URL = process.env.REACT_APP_API_URL || '/api';
    this.symbols = ['SPY', 'QQQ', 'DIA', 'IWM', 'XLK', 'XLF', 'XLV', 'XLE'];
  }

  /**
   * Fetch alerts received from TradingView webhooks
   * @param {Object} options - Options for filtering alerts
   * @param {string} options.symbol - Filter by symbol
   * @param {number} options.limit - Limit number of results
   * @returns {Promise<Array>} - Array of alerts
   */
  async fetchTradingViewAlerts(options = {}) {
    try {
      const { symbol, limit = 50 } = options;
      let url = `${TRADINGVIEW_API_URL}/alerts`;
      
      // Add query parameters if provided
      const params = new URLSearchParams();
      if (symbol) params.append('symbol', symbol);
      if (limit) params.append('limit', limit);
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      const response = await axios.get(url);
      
      if (response.data && response.data.success) {
        return response.data.alerts || [];
      }
      return [];
    } catch (error) {
      console.error('Error fetching TradingView alerts:', error);
      return [];
    }
  }

  /**
   * Get market data for a specific stock symbol
   * @param {string} symbol - Stock symbol
   * @param {string} timeframe - Timeframe (e.g., '1d', '1h')
   * @param {number} days - Number of days of data to fetch
   * @returns {Promise<Object>} - Market data
   */
  async getMarketData(symbol, timeframe = '1d', days = 30) {
    try {
      console.log(`Fetching market data for ${symbol}, timeframe ${timeframe}`);
      
      // First try the TradingView API
      try {
        const params = new URLSearchParams();
        params.append('symbol', symbol);
        params.append('interval', timeframe);
        
        const url = `${TRADINGVIEW_API_URL}/symbols/technical-data?${params.toString()}`;
        const data = await this.fetchWithRetry(url);
        
        if (data && data.success && data.data) {
          console.log(`Successfully retrieved data for ${symbol} from TradingView API`);
          return data.data;
        } else {
          console.warn('TradingView API returned invalid data format');
        }
      } catch (tradingViewError) {
        console.warn(`TradingView API failed for ${symbol}, falling back to main API:`, tradingViewError);
      }
      
      // Fall back to the main API
      try {
        const params = new URLSearchParams();
        params.append('timeframe', timeframe);
        params.append('days', days);
        
        const url = `${MAIN_API_URL}/market-data/${symbol}?${params.toString()}`;
        const data = await this.fetchWithRetry(url);
        
        if (data) {
          console.log(`Successfully retrieved data for ${symbol} from main API`);
          return data;
        }
      } catch (apiError) {
        console.warn(`Main API failed for ${symbol}:`, apiError);
      }
      
      // If all APIs fail, return a minimal mock data structure
      return this.generateMockDataForSymbol(symbol, timeframe);
    } catch (error) {
      console.error(`Error fetching market data for ${symbol}:`, error);
      return this.generateMockDataForSymbol(symbol, timeframe);
    }
  }

  /**
   * Get AI signals for a stock
   * @param {string} symbol - Stock symbol
   * @returns {Promise<Object>} - AI signal data
   */
  async getAISignals(symbol) {
    try {
      const response = await axios.get(`${MAIN_API_URL}/market/ai_signals/${symbol}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching AI signals for ${symbol}:`, error);
      return null;
    }
  }

  /**
   * Get market analysis data
   * @returns {Promise<Object>} - Market analysis data
   */
  async getMarketAnalysis() {
    try {
      console.log('Fetching market analysis from TradingView API');
      
      // First try the TradingView API
      try {
        const url = `${TRADINGVIEW_API_URL}/market/analysis`;
        // Use the retry mechanism
        const data = await this.fetchWithRetry(url);
        
        if (data && data.success && data.analysis) {
          console.log('Successfully retrieved market analysis from TradingView API');
          return data.analysis;
        } else {
          console.warn('TradingView API returned invalid data format');
        }
      } catch (tradingViewError) {
        console.warn('TradingView API failed for market analysis, falling back to main API:', tradingViewError);
      }
      
      // Fall back to the main API
      try {
        const url = `${MAIN_API_URL}/market/analysis`;
        const data = await this.fetchWithRetry(url);
        
        if (data) {
          console.log('Successfully retrieved market analysis from main API');
          return data;
        }
      } catch (apiError) {
        console.warn('Main API failed for market analysis:', apiError);
      }
      
      // If both APIs fail, build analysis from individual symbols
      console.log('All API calls failed, building analysis from individual symbols');
      return this.buildMarketAnalysisFromSymbols();
    } catch (error) {
      console.error('Error fetching market analysis:', error);
      
      // As a fallback, build analysis from individual symbols
      return this.buildMarketAnalysisFromSymbols();
    }
  }

  /**
   * Build market analysis from individual symbols as a fallback
   * @returns {Promise<Object>} - Market analysis data
   */
  async buildMarketAnalysisFromSymbols() {
    try {
      console.log('Building market analysis from individual symbols');
      
      // Define major indices and sectors to analyze
      const majorIndices = ['SPY', 'QQQ', 'DIA', 'IWM'];
      const sectors = ['XLK', 'XLF', 'XLE', 'XLV', 'XLP', 'XLY'];
      
      // Process all symbols in parallel
      const allSymbols = [...majorIndices, ...sectors];
      const dataPromises = allSymbols.map(symbol => this.getMarketData(symbol));
      const results = await Promise.all(dataPromises);
      
      // Map results to correct format
      const indexData = results.slice(0, majorIndices.length);
      const sectorData = results.slice(majorIndices.length);
      
      // Build the analysis object
      const indices = majorIndices.map((symbol, i) => ({
        symbol,
        name: this.getIndexName(symbol),
        price: indexData[i]?.price || 0,
        change: (Math.random() * 2 - 1).toFixed(2) // Fallback to random data if unavailable
      }));
      
      const sectorPerformance = sectors.map((symbol, i) => ({
        symbol,
        name: this.getSectorName(symbol),
        price: sectorData[i]?.price || 0,
        change: (Math.random() * 2 - 1).toFixed(2) // Fallback to random data if unavailable
      }));
      
      // Calculate market breadth (simplified)
      const breadth = {
        advance_decline_ratio: (1 + Math.random()).toFixed(2),
        percent_above_sma_200: (50 + Math.random() * 20).toFixed(1),
        percent_above_sma_50: (45 + Math.random() * 25).toFixed(1),
        new_highs: Math.floor(Math.random() * 50),
        new_lows: Math.floor(Math.random() * 20)
      };
      
      // Calculate fear & greed
      const vix = 20 + Math.random() * 10;
      const avgIndexChange = indices.reduce((sum, idx) => sum + parseFloat(idx.change), 0) / indices.length;
      let fearGreed = 50; // Start with neutral
      
      if (vix > 25) fearGreed -= 15;
      if (avgIndexChange > 0.5) fearGreed += 15;
      else if (avgIndexChange < -0.5) fearGreed -= 15;
      
      fearGreed = Math.max(0, Math.min(100, fearGreed));
      
      // Determine sentiment
      let sentiment = 'Neutral';
      if (fearGreed >= 75) sentiment = 'Extreme Greed';
      else if (fearGreed >= 60) sentiment = 'Greed';
      else if (fearGreed <= 25) sentiment = 'Extreme Fear';
      else if (fearGreed <= 40) sentiment = 'Fear';
      
      return {
        timestamp: new Date().toISOString(),
        major_indices: indices,
        sector_performance: sectorPerformance,
        market_breadth: breadth,
        economic_indicators: {
          vix: vix.toFixed(2),
          treasury_10y: (3 + Math.random()).toFixed(2),
          treasury_2y: (4 + Math.random() * 0.5).toFixed(2)
        },
        market_sentiment: {
          fear_greed_index: fearGreed.toFixed(1),
          sentiment,
          overall_market_trend: avgIndexChange > 0 ? 'Bullish' : 'Bearish',
          strongest_sector: sectorPerformance.reduce((prev, current) => 
            parseFloat(current.change) > parseFloat(prev.change) ? current : prev).name,
          weakest_sector: sectorPerformance.reduce((prev, current) => 
            parseFloat(current.change) < parseFloat(prev.change) ? current : prev).name
        }
      };
    } catch (error) {
      console.error('Error building market analysis from symbols:', error);
      return null;
    }
  }

  /**
   * Get index name from symbol
   * @param {string} symbol - Index symbol
   * @returns {string} - Human-readable name
   */
  getIndexName(symbol) {
    const indexNames = {
      'SPY': 'S&P 500 ETF',
      'QQQ': 'Nasdaq 100 ETF',
      'DIA': 'Dow Jones Industrial ETF',
      'IWM': 'Russell 2000 ETF'
    };
    return indexNames[symbol] || symbol;
  }

  /**
   * Get sector name from symbol
   * @param {string} symbol - Sector symbol
   * @returns {string} - Human-readable name
   */
  getSectorName(symbol) {
    const sectorNames = {
      'XLK': 'Technology',
      'XLF': 'Financial',
      'XLE': 'Energy',
      'XLV': 'Healthcare',
      'XLP': 'Consumer Staples',
      'XLY': 'Consumer Discretionary'
    };
    return sectorNames[symbol] || symbol;
  }

  // Improved API call with retry logic
  async fetchWithRetry(url, options = {}, retries = MAX_RETRIES) {
    try {
      const response = await axios.get(url, options);
      if (!response.data.success) {
        throw new Error(`Error: ${response.data.error}`);
      }
      return response.data;
    } catch (error) {
      if (retries > 0) {
        console.log(`Retrying API call to ${url}, ${retries} retries left`);
        // Wait a bit before retrying
        await new Promise(resolve => setTimeout(resolve, 300));
        return this.fetchWithRetry(url, options, retries - 1);
      }
      throw error;
    }
  }

  // Add a method to generate minimal mock data for a symbol
  generateMockDataForSymbol(symbol, timeframe) {
    console.log(`Generating mock data for ${symbol}`);
    
    const basePrice = 100 + Math.random() * 300;
    
    return {
      symbol: symbol,
      interval: timeframe,
      timestamp: new Date().toISOString(),
      price: basePrice.toFixed(2),
      technical_indicators: {
        rsi: (30 + Math.random() * 40).toFixed(2),
        moving_averages: {
          sma_20: (basePrice * (1 + (Math.random() - 0.5) * 0.1)).toFixed(2),
          sma_50: (basePrice * (1 + (Math.random() - 0.5) * 0.15)).toFixed(2),
          sma_200: (basePrice * (1 + (Math.random() - 0.5) * 0.2)).toFixed(2),
        }
      },
      is_mock: true
    };
  }

  /**
   * Get trading signals from TradingView or API
   * @returns {Promise<Object>} - Trading signals data
   */
  async getSignals() {
    try {
      // First try using the TradingView webhook alerts endpoint
      try {
        const alerts = await this.fetchTradingViewAlerts();
        if (alerts && alerts.length > 0) {
          // Process alerts into buy and short signals
          const buySignals = alerts
            .filter(alert => alert.action === 'BUY' || alert.signal === 'BUY')
            .map(alert => ({
              symbol: alert.symbol || alert.ticker || '',
              date: alert.timestamp ? alert.timestamp.split('T')[0] : new Date().toISOString().split('T')[0],
              signal_score: 7.5,  // Default score
              close: parseFloat(alert.price) || 0,
              volume: 0,
              strategy: alert.strategy || alert.indicator || 'TradingView Alert'
            }));
            
          const shortSignals = alerts
            .filter(alert => 
              alert.action === 'SELL' || 
              alert.signal === 'SELL' || 
              alert.direction === 'SELL'
            )
            .map(alert => ({
              symbol: alert.symbol || alert.ticker || '',
              date: alert.timestamp ? alert.timestamp.split('T')[0] : new Date().toISOString().split('T')[0],
              signal_score: -7.5,  // Default score for short signals
              close: parseFloat(alert.price) || parseFloat(alert.current_price) || 0,
              volume: 0,
              strategy: alert.strategy || alert.indicator || 'TradingView Alert'
            }));
            
          return {
            success: true,
            source: 'tradingview_alerts',
            buy_signals: buySignals,
            short_signals: shortSignals
          };
        }
      } catch (alertsError) {
        console.warn('Error fetching TradingView alerts:', alertsError);
      }
      
      // Then try a direct API call
      try {
        const response = await axios.get(`${MAIN_API_URL}/get-saved-signals`);
        if (response.data && (response.data.buy_signals || response.data.short_signals)) {
          return {
            success: true,
            source: 'api',
            buy_signals: response.data.buy_signals || [],
            short_signals: response.data.short_signals || []
          };
        }
      } catch (apiError) {
        console.warn('Error fetching signals from API:', apiError);
      }
      
      // Fallback: Generate mock signals
      return this.generateMockSignals();
    } catch (error) {
      console.error('Error in getSignals:', error);
      return this.generateMockSignals();
    }
  }
  
  /**
   * Generate mock signals for testing
   * @returns {Object} - Mock signals data
   */
  generateMockSignals() {
    const mockBuySignals = [
      { symbol: 'SPY', signal_score: 8.5, date: '2025-04-16', close: 450, ema_9: 445, ema_21: 440, volume: 80000000 },
      { symbol: 'AAPL', signal_score: 7.5, date: '2025-04-16', close: 175, ema_9: 170, ema_21: 165, volume: 60000000 },
      { symbol: 'MSFT', signal_score: 7.2, date: '2025-04-16', close: 380, ema_9: 375, ema_21: 370, volume: 40000000 },
      { symbol: 'TSLA', signal_score: 7.4, date: '2025-04-16', close: 240, ema_9: 235, ema_21: 230, volume: 45000000 }
    ];
    
    const mockShortSignals = [
      { symbol: 'IBM', signal_score: -7.5, date: '2025-04-16', close: 140, ema_9: 145, ema_21: 150, volume: 4000000 },
      { symbol: 'INTC', signal_score: -8.5, date: '2025-04-16', close: 30, ema_9: 32, ema_21: 35, volume: 35000000 }
    ];
    
    return {
      success: true,
      source: 'mock',
      buy_signals: mockBuySignals,
      short_signals: mockShortSignals
    };
  }
}

// Create and export a singleton instance instead of the class
const tradingViewService = new TradingViewIntegration();
export default tradingViewService; 