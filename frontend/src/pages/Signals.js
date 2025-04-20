import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Tabs, 
  Tab, 
  Card, 
  CardContent, 
  TextField,
  InputAdornment,
  CircularProgress,
  Button,
  useTheme,
  alpha,
  Divider,
  Chip,
  Alert
} from '@mui/material';
import { 
  TrendingUp, 
  TrendingDown, 
  Search, 
  Refresh,
  Sync,
  AutoAwesomeMosaic
} from '@mui/icons-material';
import axios from 'axios';
import { motion } from 'framer-motion';

import TradingSignalItem from '../components/TradingSignalItem';
import TradingViewWidget from '../components/TradingViewWidget';
import tradingViewService from '../services/TradingViewIntegration';
import { DataLabel, DataLabelContainer } from '../components/DataLabel';

const Signals = () => {
  console.log('Signals component rendering');
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [buySignals, setBuySignals] = useState([]);
  const [shortSignals, setShortSignals] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState(null);
  const [selectedSymbol, setSelectedSymbol] = useState(null);

  useEffect(() => {
    console.log('Signals component useEffect running');
    fetchSignals();
  }, []);

  const fetchSignals = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Starting to fetch signals...');
      
      let signalSource = 'mock'; // Default to mock data
      let buySignalsData = [];
      let shortSignalsData = [];
      
      // Try method 1: Using tradingViewService
      try {
        console.log('Using tradingViewService to fetch signals...');
        const signalData = await tradingViewService.getSignals();
        
        if (signalData && signalData.success) {
          console.log('Successfully loaded signals from tradingViewService');
          console.log('Signal data source:', signalData.source);
          console.log('Buy signals count:', signalData.buy_signals?.length || 0);
          console.log('Short signals count:', signalData.short_signals?.length || 0);
          
          buySignalsData = signalData.buy_signals || [];
          shortSignalsData = signalData.short_signals || [];
          signalSource = 'real';
          setBuySignals(buySignalsData);
          setShortSignals(shortSignalsData);
          return;
        } else {
          console.warn('tradingViewService returned invalid format:', signalData);
          throw new Error('Invalid signal data format');
        }
      } catch (serviceError) {
        console.warn('tradingViewService failed:', serviceError.message);
        
        // Try method 2: Fall back to legacy API call with full URL
        try {
          console.log('Falling back to legacy API call...');
          const response = await axios.get('http://localhost:5000/api/get-saved-signals');
          
          if (response.data && response.data.buy_signals && response.data.short_signals) {
            console.log('Successfully loaded signals from legacy API call');
            console.log('Buy signals count:', response.data.buy_signals.length);
            console.log('Short signals count:', response.data.short_signals.length);
            
            buySignalsData = response.data.buy_signals;
            shortSignalsData = response.data.short_signals;
            signalSource = 'real';
            setBuySignals(buySignalsData);
            setShortSignals(shortSignalsData);
            return;
          } else {
            console.warn('Legacy API returned unexpected data structure:', response.data);
            throw new Error('Legacy API returned unexpected data structure');
          }
        } catch (apiError) {
          console.warn('Legacy API call failed:', apiError.message);
          
          // Try method 3: Try dual-bot signals endpoint with full URL
          try {
            console.log('Trying dual-bot signals endpoint...');
            const dualBotResponse = await axios.get('http://localhost:5000/api/dual-bot/signals');
            
            if (dualBotResponse.data && dualBotResponse.data.success && dualBotResponse.data.signals) {
              console.log('Successfully loaded signals from dual-bot API');
              console.log('Total signals count:', dualBotResponse.data.signals.signals.length);
              
              // Split signals into buy and short based on type
              const allSignals = dualBotResponse.data.signals.signals;
              
              buySignalsData = allSignals.filter(signal => 
                signal.type === 'BUY').map(signal => ({
                  symbol: signal.symbol,
                  date: signal.time || new Date().toISOString().split('T')[0],
                  signal_score: signal.signal_score || (signal.confidence * 10),
                  close: signal.close || signal.price,
                  volume: signal.volume || 0,
                  ema_9: signal.ema_9 || signal.indicators?.ema_9 || 0,
                  ema_21: signal.ema_21 || signal.indicators?.ema_21 || 0,
                  strategy: 'Dual Bot'
                }));
              
              shortSignalsData = allSignals.filter(signal => 
                signal.type === 'SELL').map(signal => ({
                  symbol: signal.symbol,
                  date: signal.time || new Date().toISOString().split('T')[0],
                  signal_score: signal.signal_score || (signal.confidence * -10), // Make it negative for short signals
                  close: signal.close || signal.price,
                  volume: signal.volume || 0,
                  ema_9: signal.ema_9 || signal.indicators?.ema_9 || 0,
                  ema_21: signal.ema_21 || signal.indicators?.ema_21 || 0,
                  strategy: 'Dual Bot'
                }));
              
              signalSource = 'real';
              console.log('Processed buy signals:', buySignalsData.length);
              console.log('Processed short signals:', shortSignalsData.length);
              
              setBuySignals(buySignalsData);
              setShortSignals(shortSignalsData);
              return;
            } else {
              console.warn('Dual-bot API returned unexpected structure:', dualBotResponse.data);
              throw new Error('Dual-bot API returned unexpected structure');
            }
          } catch (dualBotError) {
            console.warn('Dual-bot API call failed:', dualBotError.message);
            throw dualBotError;
          }
        }
      }
    } catch (error) {
      console.error('All signal fetch methods failed:', error);
      setError(`Error loading signals: ${error.message}. Using mock data.`);
      
      // Generate mock signals
      const mockBuySignals = [
        { symbol: 'AAPL', date: new Date().toISOString().split('T')[0], signal_score: 8.5, close: 173.15, volume: 45000000, ema_9: 170.2, ema_21: 165.8, strategy: 'DeepSeek Scanner' },
        { symbol: 'MSFT', date: new Date().toISOString().split('T')[0], signal_score: 7.8, close: 291.32, volume: 32000000, ema_9: 289.5, ema_21: 285.3, strategy: 'DeepSeek Scanner' },
        { symbol: 'NVDA', date: new Date().toISOString().split('T')[0], signal_score: 9.2, close: 418.76, volume: 55000000, ema_9: 410.3, ema_21: 395.7, strategy: 'DeepSeek Scanner' }
      ];
      
      const mockShortSignals = [
        { symbol: 'TSLA', date: new Date().toISOString().split('T')[0], signal_score: -6.8, close: 212.18, volume: 75000000, ema_9: 218.6, ema_21: 230.1, strategy: 'DeepSeek Scanner' },
        { symbol: 'NFLX', date: new Date().toISOString().split('T')[0], signal_score: -5.9, close: 578.33, volume: 8000000, ema_9: 585.2, ema_21: 598.4, strategy: 'DeepSeek Scanner' }
      ];
      
      setBuySignals(mockBuySignals);
      setShortSignals(mockShortSignals);
    } finally {
      setLoading(false);
      console.log('Finished fetching signals. Loading state set to false.');
    }
  };

  const handleRefresh = () => {
    fetchSignals();
  };

  const handleGenerateSignals = async () => {
    try {
      setLoading(true);
      
      // First try the dual-bot generate endpoint with full URL
      try {
        const response = await axios.post('http://localhost:5000/api/dual-bot/generate-signals');
        if (response.data && response.data.success) {
          console.log('Successfully generated new signals via dual-bot');
          fetchSignals();
          return;
        }
      } catch (dualBotError) {
        console.warn('Failed to generate signals via dual-bot:', dualBotError.message);
      }
      
      // Fall back to legacy endpoint with full URL
      try {
        const response = await axios.post('http://localhost:5000/api/generate-signals');
        if (response.data && response.data.success) {
          console.log('Successfully generated new signals via legacy endpoint');
          fetchSignals();
          return;
        }
      } catch (legacyError) {
        console.error('Failed to generate signals via legacy endpoint:', legacyError);
        throw legacyError;
      }
    } catch (error) {
      console.error('Error generating signals:', error);
      setError(`Failed to generate signals: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleSignalClick = (signal) => {
    setSelectedSymbol(signal.symbol);
  };

  const filteredBuySignals = buySignals.filter(signal => 
    signal.symbol && signal.symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredShortSignals = shortSignals.filter(signal => 
    signal.symbol && signal.symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box sx={{ padding: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
          Trading Signals
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            startIcon={<AutoAwesomeMosaic />}
            onClick={handleGenerateSignals}
            variant="contained"
            color="secondary"
            disabled={loading}
          >
            Generate Signals
          </Button>
          <Button
            startIcon={<Refresh />}
            onClick={handleRefresh}
            variant="contained"
            color="primary"
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Box>
      
      {error && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3 }}>
        {/* Signals section */}
        <Box sx={{ flex: '1 1 auto', width: '100%' }}>
          <DataLabelContainer 
            type={buySignals.length > 0 || shortSignals.length > 0 ? 
              (error ? 'mock' : 'real') : 'mock'}
            position="topRight"
          >
            <Card sx={{ height: '100%', overflow: 'hidden', borderRadius: 2 }}>
              <Box sx={{ px: 2, pt: 2, pb: 0 }}>
                <Tabs 
                  value={activeTab} 
                  onChange={handleTabChange}
                  variant="fullWidth" 
                  indicatorColor="primary"
                  textColor="primary"
                  sx={{ mb: 2 }}
                >
                  <Tab 
                    icon={<TrendingUp />} 
                    label={`Buy Signals (${buySignals.length})`} 
                    id="tab-0"
                    aria-controls="tabpanel-0"
                  />
                  <Tab 
                    icon={<TrendingDown />} 
                    label={`Short Signals (${shortSignals.length})`} 
                    id="tab-1"
                    aria-controls="tabpanel-1"
                  />
                </Tabs>
                
                <TextField
                  fullWidth
                  placeholder="Search signals by symbol..."
                  value={searchTerm}
                  onChange={handleSearchChange}
                  variant="outlined"
                  size="small"
                  sx={{ mb: 2 }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search />
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>
              
              <Divider />
              
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
                  <CircularProgress />
                </Box>
              ) : (
                <Box 
                  role="tabpanel"
                  id={`tabpanel-${activeTab}`}
                  aria-labelledby={`tab-${activeTab}`}
                  sx={{ height: '500px', overflow: 'auto', p: 0 }}
                >
                  {activeTab === 0 ? (
                    filteredBuySignals.length > 0 ? (
                      filteredBuySignals.map((signal, index) => (
                        <motion.div
                          key={`${signal.symbol}-${index}`}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3, delay: index * 0.05 }}
                        >
                          <TradingSignalItem 
                            signal={signal} 
                            type="buy"
                            onClick={() => handleSignalClick(signal)}
                          />
                        </motion.div>
                      ))
                    ) : (
                      <Box sx={{ p: 4, textAlign: 'center' }}>
                        <Typography variant="body1" color="text.secondary">
                          No buy signals found
                        </Typography>
                      </Box>
                    )
                  ) : (
                    filteredShortSignals.length > 0 ? (
                      filteredShortSignals.map((signal, index) => (
                        <motion.div
                          key={`${signal.symbol}-${index}`}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3, delay: index * 0.05 }}
                        >
                          <TradingSignalItem 
                            signal={signal} 
                            type="short" 
                            onClick={() => handleSignalClick(signal)}
                          />
                        </motion.div>
                      ))
                    ) : (
                      <Box sx={{ p: 4, textAlign: 'center' }}>
                        <Typography variant="body1" color="text.secondary">
                          No short signals found
                        </Typography>
                      </Box>
                    )
                  )}
                </Box>
              )}
            </Card>
          </DataLabelContainer>
        </Box>
        
        {/* Chart section */}
        <Box sx={{ flex: '1 1 auto', width: '100%', minHeight: '600px' }}>
          <DataLabelContainer 
            type="real"
            tooltip="Real-time TradingView chart data"
          >
            <Card sx={{ height: '100%', borderRadius: 2 }}>
              <TradingViewWidget 
                symbol={selectedSymbol || 'AAPL'}
                autosize
              />
            </Card>
          </DataLabelContainer>
        </Box>
      </Box>
    </Box>
  );
};

export default Signals; 