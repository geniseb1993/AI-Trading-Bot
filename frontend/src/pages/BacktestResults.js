import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Button,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Divider,
  IconButton,
} from '@mui/material';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Delete, FileDownload, Refresh } from '@mui/icons-material';

// Import our new layout components
import PageLayout from '../components/PageLayout';
import ContentCard from '../components/ContentCard';
import ContentGrid from '../components/ContentGrid';

// Import chart components
import BacktestLineChart from '../components/charts/BacktestLineChart';
import BacktestBarChart from '../components/charts/BacktestBarChart';
import BacktestStatistics from '../components/BacktestStatistics';
import TradeTable from '../components/TradeTable';

const BacktestResults = () => {
  const [backtest, setBacktest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [allBacktests, setAllBacktests] = useState([]);

  useEffect(() => {
    fetchBacktests();
  }, []);

  const fetchBacktests = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/backtests');
      if (response.data && response.data.success) {
        setAllBacktests(response.data.backtests);
        if (response.data.backtests.length > 0) {
          setBacktest(response.data.backtests[0]);
        }
      } else {
        generateMockData();
      }
    } catch (error) {
      console.error('Failed to fetch backtests:', error);
      setError('Failed to fetch backtest data. Using sample data instead.');
      generateMockData();
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = () => {
    // Generate sample backtest data for demonstration
    const sampleData = {
      id: 'bt-1234',
      strategy: 'Moving Average Crossover',
      symbol: 'BTCUSDT',
      timeframe: '1h',
      startDate: '2023-01-01',
      endDate: '2023-03-31',
      initialBalance: 10000,
      finalBalance: 12345.67,
      totalReturn: 23.46,
      maxDrawdown: 15.2,
      sharpeRatio: 1.45,
      winRate: 62.5,
      trades: [
        {
          id: 1,
          timestamp: '2023-01-05T08:00:00Z',
          symbol: 'BTCUSDT',
          side: 'BUY',
          price: 16750.23,
          quantity: 0.5,
          pnl: 0,
          status: 'FILLED'
        },
        {
          id: 2,
          timestamp: '2023-01-12T16:00:00Z',
          symbol: 'BTCUSDT',
          side: 'SELL',
          price: 17840.45,
          quantity: 0.5,
          pnl: 545.11,
          status: 'FILLED'
        },
        {
          id: 3,
          timestamp: '2023-01-20T12:00:00Z',
          symbol: 'BTCUSDT',
          side: 'BUY',
          price: 17250.23,
          quantity: 0.55,
          pnl: 0,
          status: 'FILLED'
        },
        {
          id: 4,
          timestamp: '2023-02-01T10:00:00Z',
          symbol: 'BTCUSDT',
          side: 'SELL',
          price: 16840.45,
          quantity: 0.55,
          pnl: -225.43,
          status: 'FILLED'
        },
        {
          id: 5,
          timestamp: '2023-02-15T09:00:00Z',
          symbol: 'BTCUSDT',
          side: 'BUY',
          price: 21250.23,
          quantity: 0.45,
          pnl: 0,
          status: 'FILLED'
        },
        {
          id: 6,
          timestamp: '2023-03-01T14:00:00Z',
          symbol: 'BTCUSDT',
          side: 'SELL',
          price: 23840.45,
          quantity: 0.45,
          pnl: 1165.10,
          status: 'FILLED'
        }
      ],
      equityCurve: Array.from({ length: 90 }, (_, i) => {
        const day = new Date('2023-01-01');
        day.setDate(day.getDate() + i);
        // Create a somewhat realistic equity curve with some volatility
        const base = 10000 * (1 + (i * 0.3) / 100);
        const random = (Math.random() - 0.5) * 500;
        return {
          date: day.toISOString().split('T')[0],
          equity: Math.round((base + random) * 100) / 100
        };
      }),
      monthlyReturns: [
        { month: 'Jan 2023', return: 5.4 },
        { month: 'Feb 2023', return: 8.2 },
        { month: 'Mar 2023', return: 9.8 }
      ]
    };

    const sampleBacktests = [
      {
        id: 'bt-1234',
        strategy: 'Moving Average Crossover',
        symbol: 'BTCUSDT',
        timeframe: '1h',
        startDate: '2023-01-01',
        endDate: '2023-03-31',
        totalReturn: 23.46
      },
      {
        id: 'bt-5678',
        strategy: 'RSI Divergence',
        symbol: 'ETHUSDT',
        timeframe: '4h',
        startDate: '2023-02-01',
        endDate: '2023-04-30',
        totalReturn: 18.72
      },
      {
        id: 'bt-9012',
        strategy: 'Bollinger Band Breakout',
        symbol: 'ADAUSDT',
        timeframe: '1d',
        startDate: '2022-12-01',
        endDate: '2023-02-28',
        totalReturn: -5.32
      }
    ];
    
    setBacktest(sampleData);
    setAllBacktests(sampleBacktests);
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleBacktestSelect = (backtestId) => {
    const selected = allBacktests.find(bt => bt.id === backtestId);
    if (selected) {
      // In a real app, you would fetch the detailed data for this backtest
      // For now, we'll just modify our mock data
      const updatedBacktest = { ...backtest, ...selected };
      setBacktest(updatedBacktest);
    }
  };

  const downloadResults = () => {
    if (!backtest) return;
    
    // In a real app, this would be an API call to download a file
    // For demo purposes, we'll create a JSON file
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(backtest, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `backtest-${backtest.id}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const deleteBacktest = async (backtestId) => {
    try {
      // In a real app, make an API call to delete the backtest
      // const response = await axios.delete(`/api/backtests/${backtestId}`);
      
      // For demo, just remove from state
      setAllBacktests(allBacktests.filter(bt => bt.id !== backtestId));
      
      // If we deleted the currently selected backtest, select another one
      if (backtest && backtest.id === backtestId) {
        const remainingBacktests = allBacktests.filter(bt => bt.id !== backtestId);
        if (remainingBacktests.length > 0) {
          setBacktest(remainingBacktests[0]);
        } else {
          setBacktest(null);
        }
      }
    } catch (error) {
      console.error('Failed to delete backtest:', error);
      setError('Failed to delete backtest.');
      setTimeout(() => setError(null), 3000);
    }
  };

  if (loading) {
    return (
      <PageLayout>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
          <CircularProgress />
        </Box>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography 
          variant="h4" 
          component={motion.h4}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          sx={{ 
            fontWeight: 'bold',
            color: 'primary.main'
          }}
        >
          Backtest Results
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<Refresh />}
          onClick={fetchBacktests}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>
      )}

      <ContentGrid>
        <Grid item xs={12} md={3}>
          <ContentCard title="Available Backtests">
            {allBacktests.length === 0 ? (
              <Alert severity="info">No backtests available. Run a backtest to see results here.</Alert>
            ) : (
              <Box>
                {allBacktests.map((bt) => (
                  <Box 
                    key={bt.id}
                    component={motion.div}
                    whileHover={{ scale: 1.02 }}
                    sx={{ 
                      p: 2, 
                      mb: 2, 
                      borderRadius: 1, 
                      cursor: 'pointer',
                      bgcolor: backtest && backtest.id === bt.id ? 'action.selected' : 'background.paper',
                      border: '1px solid',
                      borderColor: 'divider',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                    onClick={() => handleBacktestSelect(bt.id)}
                  >
                    <Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                        {bt.strategy}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {bt.symbol} / {bt.timeframe}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {bt.startDate} - {bt.endDate}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: bt.totalReturn >= 0 ? 'success.main' : 'error.main',
                          fontWeight: 'bold' 
                        }}
                      >
                        {bt.totalReturn >= 0 ? '+' : ''}{bt.totalReturn}%
                      </Typography>
                    </Box>
                    <IconButton 
                      size="small" 
                      color="error"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteBacktest(bt.id);
                      }}
                    >
                      <Delete />
                    </IconButton>
                  </Box>
                ))}
              </Box>
            )}
          </ContentCard>
        </Grid>

        {backtest ? (
          <Grid item xs={12} md={9}>
            <ContentCard 
              title={
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                  <Typography variant="h6">{backtest.strategy} - {backtest.symbol} ({backtest.timeframe})</Typography>
                  <Button
                    variant="outlined"
                    startIcon={<FileDownload />}
                    onClick={downloadResults}
                  >
                    Download
                  </Button>
                </Box>
              }
            >
              <Tabs
                value={tabValue}
                onChange={handleTabChange}
                variant="scrollable"
                scrollButtons="auto"
                sx={{ mb: 3 }}
              >
                <Tab label="Overview" />
                <Tab label="Equity Curve" />
                <Tab label="Monthly Returns" />
                <Tab label="Trades" />
              </Tabs>

              {tabValue === 0 && (
                <ContentGrid container spacing={3}>
                  <Grid item xs={12}>
                    <BacktestStatistics backtest={backtest} />
                  </Grid>
                  <Grid item xs={12} md={8}>
                    <ContentCard title="Equity Curve" variant="outlined">
                      <BacktestLineChart 
                        data={backtest.equityCurve} 
                        xKey="date" 
                        yKey="equity" 
                        colorKey="value"
                      />
                    </ContentCard>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <ContentCard title="Monthly Returns" variant="outlined">
                      <BacktestBarChart 
                        data={backtest.monthlyReturns} 
                        xKey="month" 
                        yKey="return" 
                      />
                    </ContentCard>
                  </Grid>
                </ContentGrid>
              )}

              {tabValue === 1 && (
                <ContentCard title="Performance Over Time" variant="outlined">
                  <BacktestLineChart 
                    data={backtest.equityCurve} 
                    xKey="date" 
                    yKey="equity" 
                    colorKey="value"
                    fullSize={true}
                  />
                </ContentCard>
              )}

              {tabValue === 2 && (
                <ContentCard title="Monthly Return Analysis" variant="outlined">
                  <BacktestBarChart 
                    data={backtest.monthlyReturns} 
                    xKey="month" 
                    yKey="return"
                    fullSize={true}
                  />
                </ContentCard>
              )}

              {tabValue === 3 && (
                <ContentCard title="Trade History" variant="outlined">
                  <TradeTable trades={backtest.trades} />
                </ContentCard>
              )}
            </ContentCard>
          </Grid>
        ) : (
          <Grid item xs={12} md={9}>
            <ContentCard>
              <Alert severity="info">
                Select a backtest from the list to view detailed results or run a new backtest to analyze strategy performance.
              </Alert>
            </ContentCard>
          </Grid>
        )}
      </ContentGrid>
    </PageLayout>
  );
};

export default BacktestResults; 