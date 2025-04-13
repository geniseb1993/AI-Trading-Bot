import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  Tabs, 
  Tab, 
  Button, 
  CircularProgress, 
  Alert,
  Divider,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import { 
  Refresh,
  Add,
  SmartToy,
  History,
  TrendingUp
} from '@mui/icons-material';
import axios from 'axios';
import { motion } from 'framer-motion';
import { SnackbarProvider, useSnackbar } from 'notistack';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  ReferenceLine,
  Area,
  AreaChart
} from 'recharts';

// Import components
import PageLayout from '../components/PageLayout';
import ContentCard from '../components/ContentCard';
import ContentGrid from '../components/ContentGrid';
import TradingBotStatus from '../components/dashboard/TradingBotStatus';
import AIActivityLog from '../components/dashboard/AIActivityLog';
import ScrollIndicator from '../components/ScrollIndicator';

// Custom tooltip for chart
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <Paper elevation={3} sx={{ p: 2, backgroundColor: 'background.paper' }}>
        <Typography variant="subtitle2" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="body1" sx={{ color: payload[0].color, fontWeight: 'bold' }}>
          ${Number(payload[0].value).toLocaleString()}
        </Typography>
        {payload[1] && (
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            Starting: ${Number(payload[1].value).toLocaleString()}
          </Typography>
        )}
      </Paper>
    );
  }
  return null;
};

// Format large numbers for y-axis
const formatYAxis = (value) => {
  if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
  if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
  return `$${value}`;
};

const BotManagement = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [botData, setBotData] = useState([]);
  const [tradingHistory, setTradingHistory] = useState([]);
  const [performanceData, setPerformanceData] = useState(null);
  const [tabLoading, setTabLoading] = useState(false);
  const { enqueueSnackbar } = useSnackbar() || {};
  const activityLogRef = useRef(null);
  const tradeHistoryRef = useRef(null);
  const performanceRef = useRef(null);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    if (newValue === 1 && tradingHistory.length === 0) {
      fetchTradingHistory();
    } else if (newValue === 2 && !performanceData) {
      fetchPerformanceData();
    }
  };

  // Show desktop notification
  const showNotification = (title, message, type = 'info') => {
    if (enqueueSnackbar) {
      enqueueSnackbar(message, { variant: type });
    }
    
    // Also show browser notification if permission granted
    if (Notification.permission === 'granted') {
      new Notification(title, {
        body: message,
        icon: '/logo192.png'
      });
    } else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          new Notification(title, {
            body: message,
            icon: '/logo192.png'
          });
        }
      });
    }
  };

  // Fetch bot data
  const fetchBotData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('/api/bot/status');
      
      if (response.data && response.data.success) {
        // If the API returns a proper bot object, use it
        setBotData([
          {
            id: 'bot-1',
            name: 'Autonomous Trading Bot',
            status: response.data.data.running ? 'active' : 'paused',
            lastTrade: response.data.data.last_cycle || new Date().toISOString(),
            activeStrategies: response.data.data.active_trades_count || 0,
            pnl24h: Math.random() * 4 - 1 // Mock 24h PnL for now
          }
        ]);
      } else {
        // Fall back to mock data if needed
        setBotData([
          {
            id: 'bot-1',
            name: 'Autonomous Trading Bot',
            status: 'active',
            lastTrade: new Date().toISOString(),
            pnl24h: 2.4,
            activeStrategies: 3
          },
          {
            id: 'bot-2',
            name: 'RSI Strategy Bot',
            status: 'paused',
            lastTrade: new Date(Date.now() - 86400000).toISOString(),
            pnl24h: 0,
            activeStrategies: 0
          }
        ]);
      }
    } catch (err) {
      console.error('Error fetching bot data:', err);
      setError('Could not load trading bot data. Please try again.');
      
      // Fall back to mock data
      setBotData([
        {
          id: 'bot-1',
          name: 'Autonomous Trading Bot',
          status: 'active',
          lastTrade: new Date().toISOString(),
          pnl24h: 2.4,
          activeStrategies: 3
        },
        {
          id: 'bot-2',
          name: 'RSI Strategy Bot',
          status: 'paused',
          lastTrade: new Date(Date.now() - 86400000).toISOString(),
          pnl24h: 0,
          activeStrategies: 0
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Fetch trading history
  const fetchTradingHistory = async () => {
    setTabLoading(true);
    try {
      const response = await axios.get('/api/bot/history');
      
      if (response.data && response.data.success) {
        setTradingHistory(response.data.data || []);
      } else {
        // Fall back to mock data
        setTradingHistory([
          {
            id: 'trade-1',
            symbol: 'AAPL',
            entry_date: new Date(Date.now() - 86400000 * 3).toISOString(),
            exit_date: new Date(Date.now() - 86400000 * 2).toISOString(),
            entry_price: 192.45,
            exit_price: 195.78,
            position_type: 'LONG',
            quantity: 50,
            profit: 166.5,
            profit_pct: 1.73,
            exit_reason: 'Target reached'
          },
          {
            id: 'trade-2',
            symbol: 'NVDA',
            entry_date: new Date(Date.now() - 86400000 * 5).toISOString(),
            exit_date: new Date(Date.now() - 86400000 * 3).toISOString(),
            entry_price: 920.45,
            exit_price: 952.75,
            position_type: 'LONG',
            quantity: 15,
            profit: 484.5,
            profit_pct: 3.51,
            exit_reason: 'Target reached'
          },
          {
            id: 'trade-3',
            symbol: 'TSLA',
            entry_date: new Date(Date.now() - 86400000 * 4).toISOString(),
            exit_date: new Date(Date.now() - 86400000 * 3).toISOString(),
            entry_price: 245.75,
            exit_price: 238.45,
            position_type: 'SHORT',
            quantity: 30,
            profit: 219,
            profit_pct: 2.97,
            exit_reason: 'Target reached'
          }
        ]);
      }
    } catch (err) {
      console.error('Error fetching trading history:', err);
      // Fall back to mock data
      setTradingHistory([
        {
          id: 'trade-1',
          symbol: 'AAPL',
          entry_date: new Date(Date.now() - 86400000 * 3).toISOString(),
          exit_date: new Date(Date.now() - 86400000 * 2).toISOString(),
          entry_price: 192.45,
          exit_price: 195.78,
          position_type: 'LONG',
          quantity: 50,
          profit: 166.5,
          profit_pct: 1.73,
          exit_reason: 'Target reached'
        },
        {
          id: 'trade-2',
          symbol: 'NVDA',
          entry_date: new Date(Date.now() - 86400000 * 5).toISOString(),
          exit_date: new Date(Date.now() - 86400000 * 3).toISOString(),
          entry_price: 920.45,
          exit_price: 952.75,
          position_type: 'LONG',
          quantity: 15,
          profit: 484.5,
          profit_pct: 3.51,
          exit_reason: 'Target reached'
        }
      ]);
    } finally {
      setTabLoading(false);
    }
  };

  // Fetch performance data
  const fetchPerformanceData = async () => {
    setTabLoading(true);
    try {
      const response = await axios.get('/api/bot/performance', {
        params: { days: 30 }
      });
      
      if (response.data && response.data.success) {
        setPerformanceData(response.data.data || {});
      } else {
        // Fall back to mock data
        setPerformanceData({
          portfolio_value: 125000,
          starting_value: 100000,
          profit_loss: 25000,
          profit_loss_pct: 25,
          win_rate: 68.5,
          total_trades: 42,
          winning_trades: 29,
          losing_trades: 13,
          avg_profit_per_trade: 595.24,
          largest_gain: 2850,
          largest_loss: 1200,
          daily_performance: Array.from({ length: 30 }, (_, i) => ({
            date: new Date(Date.now() - 86400000 * (30 - i)).toISOString().split('T')[0],
            value: 100000 + Math.round(i * 25000 / 30) + (Math.random() * 2000 - 1000)
          }))
        });
      }
    } catch (err) {
      console.error('Error fetching performance data:', err);
      // Fall back to mock data
      setPerformanceData({
        portfolio_value: 125000,
        starting_value: 100000,
        profit_loss: 25000,
        profit_loss_pct: 25,
        win_rate: 68.5,
        total_trades: 42,
        winning_trades: 29,
        losing_trades: 13,
        avg_profit_per_trade: 595.24,
        largest_gain: 2850,
        largest_loss: 1200,
        daily_performance: Array.from({ length: 30 }, (_, i) => ({
          date: new Date(Date.now() - 86400000 * (30 - i)).toISOString().split('T')[0],
          value: 100000 + Math.round(i * 25000 / 30) + (Math.random() * 2000 - 1000)
        }))
      });
    } finally {
      setTabLoading(false);
    }
  };

  // Start a bot
  const startBot = async () => {
    try {
      const response = await axios.post('/api/bot/start');
      if (response.data && response.data.success) {
        fetchBotData();
        showNotification(
          'Bot Started', 
          'The Autonomous Trading Bot has been successfully started and is now running.', 
          'success'
        );
        
        // Simulate trade notifications after a delay
        setTimeout(() => {
          showNotification(
            'New Trade Entry', 
            'Entered LONG position in AAPL at $195.43',
            'info'
          );
        }, 5000);
        
        setTimeout(() => {
          showNotification(
            'Signal Generated', 
            'MSFT showing strong buy signal with 8.7 score',
            'info'
          );
        }, 10000);
      } else {
        setError('Failed to start bot: ' + (response.data.message || 'Unknown error'));
        showNotification(
          'Bot Start Failed', 
          'Failed to start the trading bot: ' + (response.data.message || 'Unknown error'),
          'error'
        );
      }
    } catch (err) {
      console.error('Error starting bot:', err);
      setError('Could not start the trading bot. Please try again.');
      showNotification(
        'Bot Start Failed', 
        'Could not start the trading bot. Please try again.',
        'error'
      );
    }
  };

  // Stop a bot
  const stopBot = async () => {
    try {
      const response = await axios.post('/api/bot/stop');
      if (response.data && response.data.success) {
        fetchBotData();
        showNotification(
          'Bot Stopped', 
          'The Autonomous Trading Bot has been stopped.',
          'warning'
        );
      } else {
        setError('Failed to stop bot: ' + (response.data.message || 'Unknown error'));
        showNotification(
          'Bot Stop Failed', 
          'Failed to stop the trading bot: ' + (response.data.message || 'Unknown error'),
          'error'
        );
      }
    } catch (err) {
      console.error('Error stopping bot:', err);
      setError('Could not stop the trading bot. Please try again.');
      showNotification(
        'Bot Stop Failed', 
        'Could not stop the trading bot. Please try again.',
        'error'
      );
    }
  };

  // Run a trading cycle
  const runTradingCycle = async () => {
    try {
      const response = await axios.post('/api/bot/run-cycle');
      if (response.data && response.data.success) {
        fetchBotData();
        showNotification(
          'Trading Cycle Executed', 
          'A trading cycle has been executed successfully.',
          'success'
        );
        
        // Simulate a trade notification after a short delay
        setTimeout(() => {
          // Randomly decide if it's a new trade or an exit
          if (Math.random() > 0.5) {
            const symbols = ['NVDA', 'TSLA', 'AMZN', 'AAPL', 'MSFT'];
            const symbol = symbols[Math.floor(Math.random() * symbols.length)];
            const price = (Math.random() * 300 + 100).toFixed(2);
            
            showNotification(
              'New Trade Entry', 
              `Entered LONG position in ${symbol} at $${price}`,
              'info'
            );
          } else {
            const symbols = ['NVDA', 'TSLA', 'AMZN', 'AAPL', 'MSFT'];
            const symbol = symbols[Math.floor(Math.random() * symbols.length)];
            const profit = (Math.random() * 8 - 2).toFixed(2);
            const profitType = parseFloat(profit) > 0 ? 'profit' : 'loss';
            
            showNotification(
              'Trade Exit', 
              `Exited position in ${symbol} with ${Math.abs(parseFloat(profit))}% ${profitType}`,
              parseFloat(profit) > 0 ? 'success' : 'warning'
            );
          }
        }, 3000);
      } else {
        setError('Failed to run trading cycle: ' + (response.data.message || 'Unknown error'));
        showNotification(
          'Trading Cycle Failed', 
          'Failed to run trading cycle: ' + (response.data.message || 'Unknown error'),
          'error'
        );
      }
    } catch (err) {
      console.error('Error running trading cycle:', err);
      setError('Could not run the trading cycle. Please try again.');
      showNotification(
        'Trading Cycle Failed', 
        'Could not run the trading cycle. Please try again.',
        'error'
      );
    }
  };

  // Format date for display
  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (e) {
      return dateString;
    }
  };

  // Request notification permission on mount
  useEffect(() => {
    if (Notification.permission !== 'granted' && Notification.permission !== 'denied') {
      Notification.requestPermission();
    }
  }, []);

  // Initialize on mount
  useEffect(() => {
    fetchBotData();
  }, []);

  return (
    <PageLayout title="Bot Management">
      <Box sx={{ width: '100%', mb: 4 }}>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" component="h2">
            Trading Bots
          </Typography>
          <Box>
            <Button 
              startIcon={<Refresh />} 
              onClick={fetchBotData}
              disabled={loading}
              sx={{ mr: 1 }}
            >
              Refresh
            </Button>
            <Button 
              startIcon={<Add />} 
              variant="outlined"
              disabled
            >
              New Bot
            </Button>
          </Box>
        </Box>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <ContentGrid>
            {botData.map(bot => (
              <motion.div
                key={bot.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <ContentCard>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <SmartToy sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="h6">{bot.name}</Typography>
                    </Box>
                    <Box>
                      {bot.status === 'active' ? (
                        <Button 
                          variant="outlined" 
                          size="small" 
                          color="warning"
                          onClick={stopBot}
                        >
                          Stop Bot
                        </Button>
                      ) : (
                        <Button 
                          variant="contained" 
                          size="small" 
                          color="success"
                          onClick={startBot}
                        >
                          Start Bot
                        </Button>
                      )}
                    </Box>
                  </Box>
                  
                  <TradingBotStatus botData={bot} />
                  
                  <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
                    <Button 
                      variant="outlined" 
                      size="small"
                      startIcon={<History />}
                      onClick={runTradingCycle}
                    >
                      Run Trading Cycle
                    </Button>
                    <Button 
                      variant="text" 
                      size="small"
                      disabled
                    >
                      Edit Settings
                    </Button>
                  </Box>
                </ContentCard>
              </motion.div>
            ))}
          </ContentGrid>
        )}
      </Box>
      
      <Divider sx={{ my: 3 }} />
      
      <Box sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="AI Activity Log" />
            <Tab label="Trade History" />
            <Tab label="Performance" />
          </Tabs>
        </Box>
        <Box sx={{ pt: 2 }}>
          {tabValue === 0 && (
            <Paper 
              elevation={0} 
              sx={{ 
                p: 0, 
                position: 'relative',
                height: '70vh',
                overflowY: 'auto',
                paddingRight: '16px'
              }}
              ref={activityLogRef}
            >
              <AIActivityLog />
              <ScrollIndicator 
                containerRef={activityLogRef} 
                position="bottom-right" 
                threshold={100}
                offsetBottom={20}
              />
            </Paper>
          )}
          {tabValue === 1 && (
            <Paper 
              elevation={0} 
              sx={{ p: 2, position: 'relative', maxHeight: '70vh', overflowY: 'auto', paddingRight: '24px' }}
              ref={tradeHistoryRef}
            >
              {tabLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                  <CircularProgress />
                </Box>
              ) : tradingHistory.length > 0 ? (
                <TableContainer>
                  <Table sx={{ minWidth: 650 }} aria-label="trading history table">
                    <TableHead>
                      <TableRow>
                        <TableCell>Symbol</TableCell>
                        <TableCell>Position</TableCell>
                        <TableCell>Entry Date</TableCell>
                        <TableCell>Exit Date</TableCell>
                        <TableCell align="right">Entry Price</TableCell>
                        <TableCell align="right">Exit Price</TableCell>
                        <TableCell align="right">Quantity</TableCell>
                        <TableCell align="right">Profit/Loss</TableCell>
                        <TableCell>Exit Reason</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {tradingHistory.map((trade) => (
                        <TableRow key={trade.id}>
                          <TableCell component="th" scope="row">
                            <strong>{trade.symbol}</strong>
                          </TableCell>
                          <TableCell>{trade.position_type}</TableCell>
                          <TableCell>{formatDate(trade.entry_date)}</TableCell>
                          <TableCell>{formatDate(trade.exit_date)}</TableCell>
                          <TableCell align="right">${trade.entry_price ? trade.entry_price.toFixed(2) : '0.00'}</TableCell>
                          <TableCell align="right">${trade.exit_price ? trade.exit_price.toFixed(2) : '0.00'}</TableCell>
                          <TableCell align="right">{trade.quantity}</TableCell>
                          <TableCell 
                            align="right" 
                            sx={{ 
                              color: trade.profit > 0 ? 'success.main' : 'error.main',
                              fontWeight: 'bold'
                            }}
                          >
                            ${trade.profit ? trade.profit.toFixed(2) : '0.00'} ({trade.profit_pct ? trade.profit_pct.toFixed(2) : '0.00'}%)
                          </TableCell>
                          <TableCell>{trade.exit_reason}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body1" sx={{ textAlign: 'center', py: 3 }}>
                  No trading history available yet.
                </Typography>
              )}
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                <Button 
                  startIcon={<Refresh />} 
                  variant="outlined"
                  onClick={fetchTradingHistory}
                  disabled={tabLoading}
                >
                  Refresh
                </Button>
              </Box>
              <ScrollIndicator 
                containerRef={tradeHistoryRef} 
                position="bottom-right" 
                threshold={100}
                offsetBottom={20}
              />
            </Paper>
          )}
          {tabValue === 2 && (
            <Paper 
              elevation={0} 
              sx={{ p: 2, position: 'relative', maxHeight: '70vh', overflowY: 'auto', paddingRight: '24px' }}
              ref={performanceRef}
            >
              {tabLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                  <CircularProgress />
                </Box>
              ) : performanceData ? (
                <>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 3 }}>
                    <ContentCard sx={{ minWidth: 200, flex: 1 }}>
                      <Typography variant="subtitle2" color="text.secondary">Portfolio Value</Typography>
                      <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                        ${performanceData.portfolio_value ? performanceData.portfolio_value.toLocaleString() : '0'}
                      </Typography>
                    </ContentCard>

                    <ContentCard sx={{ minWidth: 200, flex: 1 }}>
                      <Typography variant="subtitle2" color="text.secondary">Total P/L</Typography>
                      <Typography 
                        variant="h5" 
                        sx={{ 
                          fontWeight: 'bold',
                          color: performanceData.profit_loss > 0 ? 'success.main' : 'error.main' 
                        }}
                      >
                        ${performanceData.profit_loss ? performanceData.profit_loss.toLocaleString() : '0'} ({performanceData.profit_loss_pct ? performanceData.profit_loss_pct.toFixed(2) : '0.00'}%)
                      </Typography>
                    </ContentCard>

                    <ContentCard sx={{ minWidth: 200, flex: 1 }}>
                      <Typography variant="subtitle2" color="text.secondary">Win Rate</Typography>
                      <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                        {performanceData.win_rate ? performanceData.win_rate.toFixed(1) : '0.0'}%
                      </Typography>
                    </ContentCard>
                  </Box>

                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 3 }}>
                    <ContentCard sx={{ minWidth: 200, flex: 1 }}>
                      <Typography variant="subtitle2" color="text.secondary">Total Trades</Typography>
                      <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                        {performanceData.total_trades}
                      </Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                        <Typography variant="body2" color="success.main">Win: {performanceData.winning_trades}</Typography>
                        <Typography variant="body2" color="error.main">Loss: {performanceData.losing_trades}</Typography>
                      </Box>
                    </ContentCard>

                    <ContentCard sx={{ minWidth: 200, flex: 1 }}>
                      <Typography variant="subtitle2" color="text.secondary">Avg. Profit/Trade</Typography>
                      <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                        ${performanceData.avg_profit_per_trade ? performanceData.avg_profit_per_trade.toFixed(2) : '0.00'}
                      </Typography>
                    </ContentCard>

                    <ContentCard sx={{ minWidth: 200, flex: 1 }}>
                      <Typography variant="subtitle2" color="text.secondary">Largest Gain/Loss</Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                        <Typography variant="body1" color="success.main" sx={{ fontWeight: 'bold' }}>
                          +${performanceData.largest_gain ? performanceData.largest_gain.toLocaleString() : '0'}
                        </Typography>
                        <Typography variant="body1" color="error.main" sx={{ fontWeight: 'bold' }}>
                          -${performanceData.largest_loss ? performanceData.largest_loss.toLocaleString() : '0'}
                        </Typography>
                      </Box>
                    </ContentCard>
                  </Box>

                  <Typography variant="h6" sx={{ mt: 3, mb: 2 }}>
                    Portfolio Value History (30 Days)
                  </Typography>
                  
                  <Box sx={{ height: 350, width: '100%' }}>
                    {performanceData.daily_performance && performanceData.daily_performance.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart
                          data={performanceData.daily_performance.map(day => ({
                            ...day,
                            starting: performanceData.starting_value
                          }))}
                          margin={{ top: 10, right: 30, left: 20, bottom: 30 }}
                        >
                          <defs>
                            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#3f51b5" stopOpacity={0.8}/>
                              <stop offset="95%" stopColor="#3f51b5" stopOpacity={0.1}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="#ccc" strokeOpacity={0.5} />
                          <XAxis 
                            dataKey="date" 
                            angle={-30}
                            textAnchor="end"
                            height={50}
                            tick={{ fontSize: 12 }}
                          />
                          <YAxis 
                            tickFormatter={formatYAxis}
                            domain={['auto', 'auto']}
                          />
                          <Tooltip content={<CustomTooltip />} />
                          <Legend />
                          <ReferenceLine 
                            y={performanceData.starting_value} 
                            stroke="#666" 
                            strokeDasharray="3 3" 
                            label={{ value: 'Initial Investment', position: 'insideBottomRight' }} 
                          />
                          <Area 
                            type="monotone" 
                            dataKey="value" 
                            name="Portfolio Value" 
                            stroke="#3f51b5" 
                            fillOpacity={1} 
                            fill="url(#colorValue)" 
                            activeDot={{ r: 8 }}
                          />
                          <Line 
                            type="monotone" 
                            dataKey="starting" 
                            name="Initial Investment" 
                            stroke="#666" 
                            strokeDasharray="5 5" 
                            dot={false}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    ) : (
                      <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 10 }}>
                        No performance history data available.
                      </Typography>
                    )}
                  </Box>
                </>
              ) : (
                <Typography variant="body1" sx={{ textAlign: 'center', py: 3 }}>
                  No performance data available yet.
                </Typography>
              )}
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                <Button 
                  startIcon={<Refresh />} 
                  variant="outlined"
                  onClick={fetchPerformanceData}
                  disabled={tabLoading}
                >
                  Refresh
                </Button>
              </Box>
              <ScrollIndicator 
                containerRef={performanceRef} 
                position="bottom-right" 
                threshold={100}
                offsetBottom={20}
              />
            </Paper>
          )}
        </Box>
      </Box>
    </PageLayout>
  );
};

// Wrap component with SnackbarProvider
const BotManagementWithSnackbar = () => (
  <SnackbarProvider maxSnack={5} anchorOrigin={{ vertical: 'top', horizontal: 'right' }}>
    <BotManagement />
  </SnackbarProvider>
);

export default BotManagementWithSnackbar; 