import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Grid,
  CircularProgress,
  Button,
  useTheme,
  alpha,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  MenuItem,
  Container,
  CardHeader,
  Divider,
  Tabs,
  Tab
} from '@mui/material';
import { 
  Refresh, 
  Assessment,
  PlayArrow,
  BarChart,
  Settings,
  ViewList,
  Analytics
} from '@mui/icons-material';
import { ResponsiveLine } from '@nivo/line';
import axios from 'axios';
import { motion } from 'framer-motion';

// Import our new layout components
import PageLayout from '../components/PageLayout';
import ContentCard from '../components/ContentCard';
import ContentGrid from '../components/ContentGrid';

const Backtest = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [backtestResults, setBacktestResults] = useState([]);
  const [performanceMetrics, setPerformanceMetrics] = useState({
    totalTrades: 0,
    winRate: 0,
    longWinRate: 0,
    shortWinRate: 0,
    profitFactor: 0,
    averageProfit: 0,
    averageWin: 0,
    averageLoss: 0,
    maxDrawdown: 0,
    maxDrawdownPercent: 0,
    sharpeRatio: 0,
    totalNetProfit: 0
  });
  const [equityCurveData, setEquityCurveData] = useState([]);
  const [cumulativeWinLossData, setCumulativeWinLossData] = useState([]);
  const [timeframe, setTimeframe] = useState('all');
  const [apiConnected, setApiConnected] = useState(false);
  const [dataSource, setDataSource] = useState('sample'); // 'api', 'csv', or 'sample'

  useEffect(() => {
    fetchBacktestResults();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchBacktestResults = async () => {
    try {
      setLoading(true);
      
      // Try to fetch from API
      try {
        const response = await axios.get('/api/get-backtest-results');
        if (response.data.success) {
          const results = response.data.backtest_results;
          setBacktestResults(results);
          setApiConnected(true);
          setDataSource('api');
          
          // Process data for visualization
          processBacktestData(results);
        }
      } catch (apiError) {
        console.log('Error fetching from API:', apiError);
        setApiConnected(false);
        
        // Try to load CSV file directly
        try {
          const csvResponse = await axios.get('/backtest_results.csv');
          
          if (csvResponse.data) {
            // Parse CSV data
            const parsedData = parseCSV(csvResponse.data);
            setBacktestResults(parsedData);
            setDataSource('csv');
            
            // Process data for visualization
            processBacktestData(parsedData);
          } else {
            throw new Error('CSV file not properly loaded');
          }
        } catch (csvError) {
          console.log('Using sample backtest data:', csvError);
          setDataSource('sample');
          // Generate sample data
          const sampleData = generateSampleData();
          setBacktestResults(sampleData);
          processBacktestData(sampleData);
        }
      }
    } catch (error) {
      console.error('Error fetching backtest results:', error);
    } finally {
      setLoading(false);
    }
  };

  // Helper function to parse CSV data
  const parseCSV = (csvText) => {
    const lines = csvText.split('\n');
    const headers = lines[0].split(',');
    
    // First parse the raw CSV data
    const rawData = lines.slice(1)
      .filter(line => line.trim() !== '')
      .map(line => {
        const values = line.split(',');
        const entry = {};
        
        headers.forEach((header, index) => {
          entry[header] = values[index];
        });
        
        return entry;
      });
    
    // Then process it into trades
    const trades = [];
    let entryData = null;
    
    // Group entry/exit pairs into trades
    for (const entry of rawData) {
      // Determine if this is an entry or exit
      const isEntry = entry.action === 'BUY' || entry.action === 'SHORT';
      const isExit = entry.action === 'SELL' || entry.action === 'COVER';
      
      if (isEntry) {
        entryData = entry;
        // Check if trade direction is specified, otherwise infer from action
        entryData.direction = entry.direction || (entry.action === 'BUY' ? 'long' : 'short');
      } else if (isExit && entryData) {
        // We have a complete trade
        let profit;
        
        // Calculate profit based on direction
        if (entryData.direction === 'long') {
          profit = (parseFloat(entry.price) - parseFloat(entryData.price)) * parseFloat(entry.quantity);
        } else {
          // For short trades, profit is reversed
          profit = (parseFloat(entryData.price) - parseFloat(entry.price)) * parseFloat(entry.quantity);
        }
        
        // Determine if stop loss or take profit was hit
        let exitReason = entry.exit_reason || '';
        if (!exitReason) {
          exitReason = profit > 0 ? 'take_profit' : 'stop_loss';
        }
        
        trades.push({
          symbol: entry.symbol || entryData.symbol || 'UNKNOWN',
          entry_date: entryData.timestamp.split(' ')[0],
          exit_date: entry.timestamp.split(' ')[0],
          entry_price: parseFloat(entryData.price),
          exit_price: parseFloat(entry.price),
          quantity: parseFloat(entry.quantity),
          profit: parseFloat(profit.toFixed(2)),
          trade_outcome: profit > 0 ? 'win' : 'loss',
          direction: entryData.direction,
          // If stop loss and take profit are in the data, use them
          stop_loss: entry.stop_loss || entryData.stop_loss || 
            (entryData.direction === 'long' 
              ? parseFloat(entryData.price) * 0.95 
              : parseFloat(entryData.price) * 1.05).toFixed(2),
          take_profit: entry.take_profit || entryData.take_profit || 
            (entryData.direction === 'long' 
              ? parseFloat(entryData.price) * 1.15 
              : parseFloat(entryData.price) * 0.85).toFixed(2),
          exit_reason: exitReason
        });
        
        entryData = null;
      }
    }
    
    return trades;
  };

  const generateSampleData = () => {
    // Generate sample backtest data for demo
    const symbols = ['SPY', 'QQQ', 'TSLA'];
    const results = [];
    
    for (let i = 0; i < 20; i++) {
      const isWin = Math.random() > 0.3;
      const symbol = symbols[Math.floor(Math.random() * symbols.length)];
      const entryPrice = parseFloat((Math.random() * 100 + 100).toFixed(2));
      
      // Add trade direction (long or short)
      const direction = Math.random() > 0.4 ? 'long' : 'short';
      
      // Calculate exit price based on direction and outcome
      let exitPrice, profit;
      
      if (direction === 'long') {
        exitPrice = isWin 
          ? parseFloat((entryPrice * (1 + Math.random() * 0.1)).toFixed(2))
          : parseFloat((entryPrice * (1 - Math.random() * 0.05)).toFixed(2));
        profit = parseFloat((exitPrice - entryPrice).toFixed(2));
      } else {
        // For short trades, profit is made when price goes down
        exitPrice = isWin 
          ? parseFloat((entryPrice * (1 - Math.random() * 0.1)).toFixed(2))
          : parseFloat((entryPrice * (1 + Math.random() * 0.05)).toFixed(2));
        profit = parseFloat((entryPrice - exitPrice).toFixed(2));
      }
      
      const entryDate = new Date();
      entryDate.setDate(entryDate.getDate() - 20 + i);
      
      const exitDate = new Date(entryDate);
      exitDate.setDate(exitDate.getDate() + Math.floor(Math.random() * 5) + 1);
      
      // Add stop loss and take profit levels
      const stopLoss = direction === 'long' 
        ? parseFloat((entryPrice * 0.95).toFixed(2))
        : parseFloat((entryPrice * 1.05).toFixed(2));
        
      const takeProfit = direction === 'long'
        ? parseFloat((entryPrice * 1.1).toFixed(2))
        : parseFloat((entryPrice * 0.9).toFixed(2));
      
      // Determine if stop loss or take profit was hit
      const exitReason = isWin ? 'take_profit' : 'stop_loss';
      
      results.push({
        symbol,
        entry_date: entryDate.toISOString().split('T')[0],
        exit_date: exitDate.toISOString().split('T')[0],
        entry_price: entryPrice,
        exit_price: exitPrice,
        profit,
        trade_outcome: isWin ? 'win' : 'loss',
        direction,
        stop_loss: stopLoss,
        take_profit: takeProfit,
        exit_reason: exitReason,
        quantity: Math.floor(Math.random() * 50) + 10
      });
    }
    
    return results;
  };

  const processBacktestData = (results) => {
    // Calculate performance metrics
    if (results.length === 0) {
      return;
    }
    
    // For CSV data, we might need to process it differently
    let processedResults = results;
    
    // Check if the data is in raw CSV format
    if (results.length > 0 && results[0].hasOwnProperty('action')) {
      processedResults = parseCSV(results);
    }
    
    // Filter out any null trades
    const trades = processedResults.filter(result => result.trade_outcome !== null);
    
    // Separate by direction
    const longTrades = trades.filter(trade => trade.direction === 'long' || !trade.direction);
    const shortTrades = trades.filter(trade => trade.direction === 'short');
    
    // Calculate win rates
    const winningTrades = trades.filter(trade => parseFloat(trade.profit) > 0);
    const winningLongTrades = longTrades.filter(trade => parseFloat(trade.profit) > 0);
    const winningShortTrades = shortTrades.filter(trade => parseFloat(trade.profit) > 0);
    
    const totalTrades = trades.length;
    const winRate = totalTrades > 0 ? (winningTrades.length / totalTrades) * 100 : 0;
    const longWinRate = longTrades.length > 0 ? (winningLongTrades.length / longTrades.length) * 100 : 0;
    const shortWinRate = shortTrades.length > 0 ? (winningShortTrades.length / shortTrades.length) * 100 : 0;
    
    // Calculate profit metrics
    const totalProfit = trades.reduce((sum, trade) => sum + parseFloat(trade.profit || 0), 0);
    const totalLoss = Math.abs(trades.filter(trade => parseFloat(trade.profit) < 0).reduce((sum, trade) => sum + parseFloat(trade.profit || 0), 0));
    const profitFactor = totalLoss > 0 ? totalProfit / totalLoss : totalProfit;
    
    const averageProfit = totalTrades > 0 ? totalProfit / totalTrades : 0;
    
    // Calculate average win and loss
    const averageWin = winningTrades.length > 0 
      ? winningTrades.reduce((sum, trade) => sum + parseFloat(trade.profit), 0) / winningTrades.length 
      : 0;
      
    const averageLoss = totalTrades - winningTrades.length > 0 
      ? trades
          .filter(trade => parseFloat(trade.profit) < 0)
          .reduce((sum, trade) => sum + Math.abs(parseFloat(trade.profit)), 0) / (totalTrades - winningTrades.length) 
      : 0;
    
    // Calculate max drawdown
    let maxEquity = 10000; // Starting equity
    let currentDrawdown = 0;
    let maxDrawdown = 0;
    let maxDrawdownPercent = 0;
    
    // Calculate equity curve data
    let equity = 10000; // Starting equity
    const equityPoints = [];
    const dailyReturns = [];
    let prevEquity = equity;
    
    // Calculate cumulative win/loss data
    let cumulativeWins = 0;
    let cumulativeLosses = 0;
    const cumulativeWinLossPoints = [];
    
    trades.forEach((result, index) => {
      if (result.profit) {
        equity += parseFloat(result.profit);
        
        // Update win/loss counts
        if (parseFloat(result.profit) > 0) {
          cumulativeWins++;
        } else {
          cumulativeLosses++;
        }
      }
      
      // Calculate daily return for Sharpe ratio
      const dailyReturn = (equity - prevEquity) / prevEquity;
      dailyReturns.push(dailyReturn);
      prevEquity = equity;
      
      equityPoints.push({
        x: index.toString(),
        y: equity
      });
      
      cumulativeWinLossPoints.push({
        x: index.toString(),
        wins: cumulativeWins,
        losses: cumulativeLosses,
        total: index + 1,
        winRate: ((cumulativeWins / (index + 1)) * 100).toFixed(1)
      });
      
      if (equity > maxEquity) {
        maxEquity = equity;
        currentDrawdown = 0;
      } else {
        currentDrawdown = maxEquity - equity;
        const currentDrawdownPercent = (currentDrawdown / maxEquity) * 100;
        
        if (currentDrawdown > maxDrawdown) {
          maxDrawdown = currentDrawdown;
          maxDrawdownPercent = currentDrawdownPercent;
        }
      }
    });
    
    // Calculate Sharpe Ratio (assuming risk-free rate of 0%)
    const meanDailyReturn = dailyReturns.reduce((sum, return_) => sum + return_, 0) / dailyReturns.length;
    const stdDailyReturn = Math.sqrt(
      dailyReturns.reduce((sum, return_) => sum + Math.pow(return_ - meanDailyReturn, 2), 0) / dailyReturns.length
    );
    const sharpeRatio = stdDailyReturn !== 0 ? (meanDailyReturn / stdDailyReturn) * Math.sqrt(252) : 0; // Annualized
    
    setPerformanceMetrics({
      totalTrades,
      winRate: winRate.toFixed(2),
      longWinRate: longWinRate.toFixed(2),
      shortWinRate: shortWinRate.toFixed(2),
      profitFactor: profitFactor.toFixed(2),
      averageProfit: averageProfit.toFixed(2),
      averageWin: averageWin.toFixed(2),
      averageLoss: averageLoss.toFixed(2),
      maxDrawdown: maxDrawdown.toFixed(2),
      maxDrawdownPercent: maxDrawdownPercent.toFixed(2),
      sharpeRatio: sharpeRatio.toFixed(2),
      totalNetProfit: totalProfit.toFixed(2)
    });
    
    setEquityCurveData([{
      id: 'Equity Curve',
      color: theme.palette.primary.main,
      data: equityPoints
    }]);
    
    setCumulativeWinLossData([
      {
        id: 'Win Rate',
        color: theme.palette.success.main,
        data: cumulativeWinLossPoints.map(point => ({
          x: point.x,
          y: parseFloat(point.winRate)
        }))
      }
    ]);
    
    // Update backtestResults if we processed the CSV format
    if (results.length > 0 && results[0].hasOwnProperty('action')) {
      setBacktestResults(processedResults);
    }
  };

  const handleRefresh = () => {
    fetchBacktestResults();
  };

  const handleTimeframeChange = (event) => {
    setTimeframe(event.target.value);
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        {/* Header with title and refresh button */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography 
          variant="h4" 
            component={motion.div}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          sx={{ 
              fontFamily: 'Orbitron',
              color: theme.palette.primary.main,
              display: 'flex',
              alignItems: 'center',
              gap: 1
            }}
          >
            <Assessment fontSize="large" />
            Backtest Dashboard
            </Typography>
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              select
              size="small"
              label="Time Period"
              value={timeframe}
              onChange={handleTimeframeChange}
              sx={{ minWidth: 150 }}
            >
              <MenuItem value="all">All Data</MenuItem>
              <MenuItem value="1m">Last Month</MenuItem>
              <MenuItem value="3m">Last 3 Months</MenuItem>
              <MenuItem value="6m">Last 6 Months</MenuItem>
              <MenuItem value="1y">Last Year</MenuItem>
            </TextField>
            
        <Button 
          variant="contained" 
          color="primary" 
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Refresh />}
          onClick={handleRefresh}
              disabled={loading}
          sx={{ fontFamily: 'Orbitron' }}
        >
              Refresh Data
        </Button>
      </Box>
        </Box>

        {/* Tabs Navigation */}
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange}
                sx={{ 
            mb: 3,
            '& .MuiTab-root': {
              fontFamily: 'Orbitron',
              fontSize: '0.9rem',
            },
            '& .Mui-selected': {
              color: theme.palette.primary.main,
            },
            '& .MuiTabs-indicator': {
              backgroundColor: theme.palette.primary.main,
            }
          }}
        >
          <Tab 
            label="Performance Dashboard" 
            icon={<BarChart />} 
            iconPosition="start"
          />
          <Tab 
            label="Trade Analytics" 
            icon={<Analytics />} 
            iconPosition="start"
          />
          <Tab 
            label="Trade List" 
            icon={<ViewList />} 
            iconPosition="start"
          />
          <Tab 
            label="Backtest Settings" 
            icon={<Settings />} 
            iconPosition="start"
          />
        </Tabs>

        {loading ? (
          <Box 
            sx={{ 
                      display: 'flex', 
              flexDirection: 'column', 
              justifyContent: 'center', 
                      alignItems: 'center',
              height: '70vh',
              backgroundColor: alpha(theme.palette.background.paper, 0.7),
              backdropFilter: 'blur(10px)',
              borderRadius: 2,
              p: 4
            }}
          >
            <CircularProgress size={50} sx={{ mb: 3, color: theme.palette.primary.main }} />
            <Typography variant="h6" color="text.secondary" sx={{ fontFamily: 'Orbitron' }}>
              Loading backtest data...
                      </Typography>
                    </Box>
        ) : (
          <Box sx={{ minHeight: '600px' }}>
            {/* Performance Dashboard Tab */}
            {activeTab === 0 && (
              <Card 
                sx={{ 
                  minHeight: '600px',
                  backgroundColor: alpha(theme.palette.background.paper, 0.7),
                  backdropFilter: 'blur(10px)',
                  borderRadius: 2,
                  overflow: 'hidden',
                  boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.2)}, 0 0 8px ${alpha(theme.palette.primary.main, 0.2)}`,
                      display: 'flex', 
                  flexDirection: 'column',
                  position: 'relative'
                }}
              >
                <CardHeader 
                  title="Performance Dashboard" 
                  titleTypographyProps={{ 
                    fontFamily: 'Orbitron',
                    fontSize: '1.1rem'
                  }} 
                  sx={{ 
                    borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                    flexShrink: 0,
                    position: 'relative',
                    zIndex: 5
                  }}
                />
                <CardContent 
                  sx={{ 
                    p: 2, 
                    flexGrow: 1, 
                    overflow: 'auto',
                    position: 'relative',
                    height: 'calc(100% - 64px)', // 64px is CardHeader height
                    '&:last-child': { pb: 2 }
                  }}
                >
                  <Box 
                    sx={{ 
                      display: 'flex', 
                      flexDirection: 'column', 
                      gap: 3,
                      width: '100%'
                    }}
                  >
                    {/* Performance Metrics - Summary row at the top */}
                    <Box 
                      sx={{ 
                        p: 3, 
                        bgcolor: alpha(theme.palette.background.paper, 0.5),
                        borderRadius: 2,
                      }}
                    >
                      <Typography variant="h6" sx={{ mb: 3, fontFamily: 'Orbitron' }}>Trading Performance</Typography>
                      
                      <Grid container spacing={3}>
                        <Grid item xs={12} sm={6} md={3}>
                          <Box sx={{ mb: { xs: 2, md: 0 } }}>
                            <Typography variant="subtitle2" color="text.secondary">
                              Total Trades
                            </Typography>
                            <Typography variant="h4" fontWeight="bold">
                              {performanceMetrics.totalTrades}
                      </Typography>
                    </Box>
                        </Grid>
                        
                        <Grid item xs={12} sm={6} md={3}>
                          <Box sx={{ mb: { xs: 2, md: 0 } }}>
                            <Typography variant="subtitle2" color="text.secondary">
                              Win Rate
                            </Typography>
                            <Typography variant="h4" fontWeight="bold" 
                              color={parseFloat(performanceMetrics.winRate) > 50 ? 'success.main' : 'error.main'}>
                              {performanceMetrics.winRate}%
                      </Typography>
                    </Box>
                        </Grid>
                        
                        <Grid item xs={12} sm={6} md={3}>
                          <Box sx={{ mb: { xs: 2, md: 0 } }}>
                            <Typography variant="subtitle2" color="text.secondary">
                              Profit Factor
                            </Typography>
                            <Typography variant="h4" fontWeight="bold"
                              color={parseFloat(performanceMetrics.profitFactor) > 1 ? 'success.main' : 'error.main'}>
                              {performanceMetrics.profitFactor}
                      </Typography>
                    </Box>
                        </Grid>
                        
                        <Grid item xs={12} sm={6} md={3}>
                          <Box>
                            <Typography variant="subtitle2" color="text.secondary">
                              Net Profit
                            </Typography>
                            <Typography variant="h4" fontWeight="bold"
                              color={parseFloat(performanceMetrics.totalNetProfit) > 0 ? 'success.main' : 'error.main'}>
                        ${performanceMetrics.totalNetProfit}
                      </Typography>
                    </Box>
            </Grid>
                      </Grid>
                    </Box>
                    
                    {/* Equity Curve - Full width, large height box */}
                    <Box 
                sx={{ 
                        height: 600,
                        bgcolor: alpha(theme.palette.background.paper, 0.5),
                        borderRadius: 2,
                        p: 3,
                        position: 'relative',
                        overflow: 'hidden'
                      }}
                    >
                      <Typography variant="h6" sx={{ mb: 2, fontFamily: 'Orbitron' }}>Equity Curve</Typography>
                      <Box 
                        sx={{ 
                          position: 'absolute',
                          top: 60,
                          left: 0,
                          right: 0,
                          bottom: 0,
                          padding: '0 20px 20px 20px'
                        }}
                      >
                      <ResponsiveLine
                        data={equityCurveData}
                          margin={{ top: 40, right: 40, bottom: 60, left: 80 }}
                        xScale={{ type: 'point' }}
                        yScale={{
                          type: 'linear',
                          min: 'auto',
                          max: 'auto',
                            stacked: false,
                            reverse: false
                        }}
                        axisBottom={{
                          tickSize: 5,
                          tickPadding: 5,
                          tickRotation: 0,
                          legend: 'Trades',
                            legendOffset: 45,
                          legendPosition: 'middle'
                        }}
                        axisLeft={{
                          tickSize: 5,
                          tickPadding: 5,
                          tickRotation: 0,
                          legend: 'Equity ($)',
                            legendOffset: -60,
                          legendPosition: 'middle'
                        }}
                          curve="monotoneX"
                          colors={{ scheme: 'category10' }}
                          pointSize={8}
                        pointColor={{ theme: 'background' }}
                        pointBorderWidth={2}
                        pointBorderColor={{ from: 'serieColor' }}
                        enableArea={true}
                        areaOpacity={0.15}
                        enableGridX={false}
                          enableSlices="x"
                          enableResponsive={true}
                          useMesh={true}
                          animate={false}
                          isInteractive={true}
                          legends={[]}
                          enableCrosshair={true}
                          motionConfig="gentle"
                          defs={[
                            {
                              id: 'gradientA',
                              type: 'linearGradient',
                              colors: [
                                { offset: 0, color: alpha(theme.palette.primary.main, 0) },
                                { offset: 100, color: alpha(theme.palette.primary.main, 0.3) }
                              ]
                            }
                          ]}
                          fill={[{ match: '*', id: 'gradientA' }]}
                        theme={{
                          axis: {
                            ticks: {
                              text: {
                                fill: theme.palette.text.secondary,
                                  fontSize: 12,
                              },
                            },
                            legend: {
                              text: {
                                fill: theme.palette.text.primary,
                                  fontSize: 14,
                                  fontWeight: 'bold',
                              },
                            },
                          },
                          grid: {
                            line: {
                                stroke: alpha(theme.palette.divider, 0.2),
                                strokeWidth: 1,
                            },
                          },
                          crosshair: {
                            line: {
                              stroke: theme.palette.primary.main,
                              strokeWidth: 1,
                                strokeOpacity: 0.5,
                            },
                          },
                          tooltip: {
                            container: {
                              background: theme.palette.background.paper,
                              color: theme.palette.text.primary,
                                fontSize: 12,
                                borderRadius: 4,
                                boxShadow: theme.shadows[3],
                                padding: 12,
                            },
                          },
                        }}
                      />
                      </Box>
                  </Box>
                    
                    {/* Win Rate Over Time - Full width, large height box */}
                    <Box 
            sx={{ 
                        height: 600,
                        bgcolor: alpha(theme.palette.background.paper, 0.5),
                        borderRadius: 2,
                        p: 3,
                        position: 'relative',
                        overflow: 'hidden'
                      }}
                    >
                      <Typography variant="h6" sx={{ mb: 2, fontFamily: 'Orbitron' }}>Win Rate Over Time</Typography>
                      <Box 
                            sx={{ 
                          position: 'absolute',
                          top: 60,
                          left: 0,
                          right: 0,
                          bottom: 0,
                          padding: '0 20px 20px 20px'
                        }}
                      >
                        <ResponsiveLine
                          data={cumulativeWinLossData}
                          margin={{ top: 40, right: 40, bottom: 60, left: 80 }}
                          xScale={{ type: 'point' }}
                          yScale={{
                            type: 'linear',
                            min: 0,
                            max: 100,
                            stacked: false,
                            reverse: false
                          }}
                          axisBottom={{
                            tickSize: 5,
                            tickPadding: 5,
                            tickRotation: 0,
                            legend: 'Trades',
                            legendOffset: 45,
                            legendPosition: 'middle'
                          }}
                          axisLeft={{
                            tickSize: 5,
                            tickPadding: 5,
                            tickRotation: 0,
                            legend: 'Win Rate (%)',
                            legendOffset: -60,
                            legendPosition: 'middle'
                          }}
                          curve="monotoneX"
                          lineWidth={3}
                          colors={[theme.palette.success.main]}
                          pointSize={8}
                          pointColor={{ theme: 'background' }}
                          pointBorderWidth={2}
                          pointBorderColor={{ from: 'serieColor' }}
                          enableArea={true}
                          areaOpacity={0.15}
                          enableSlices="x"
                          enableGridX={false}
                          enableResponsive={true}
                          useMesh={true}
                          animate={false}
                          isInteractive={true}
                          legends={[]}
                          enableCrosshair={true}
                          motionConfig="gentle"
                          defs={[
                            {
                              id: 'gradientB',
                              type: 'linearGradient',
                              colors: [
                                { offset: 0, color: alpha(theme.palette.success.main, 0) },
                                { offset: 100, color: alpha(theme.palette.success.main, 0.3) }
                              ]
                            }
                          ]}
                          fill={[{ match: '*', id: 'gradientB' }]}
                          theme={{
                            axis: {
                              ticks: {
                                text: {
                                  fill: theme.palette.text.secondary,
                                  fontSize: 12,
                                },
                              },
                              legend: {
                                text: {
                                  fill: theme.palette.text.primary,
                                  fontSize: 14,
                                fontWeight: 'bold',
                                },
                              },
                            },
                            grid: {
                              line: {
                                stroke: alpha(theme.palette.divider, 0.2),
                                strokeWidth: 1,
                              },
                            },
                            crosshair: {
                              line: {
                                stroke: theme.palette.primary.main,
                                strokeWidth: 1,
                                strokeOpacity: 0.5,
                              },
                            },
                            tooltip: {
                              container: {
                                background: theme.palette.background.paper,
                                color: theme.palette.text.primary,
                                fontSize: 12,
                                borderRadius: 4,
                                boxShadow: theme.shadows[3],
                                padding: 12,
                              },
                            },
                          }}
                        />
                              </Box>
                              </Box>
                  </Box>
            </CardContent>
          </Card>
            )}
          
            {/* Trade Analytics Tab */}
            {activeTab === 1 && (
          <Card 
            sx={{ 
                  minHeight: '600px',
              backgroundColor: alpha(theme.palette.background.paper, 0.7),
              backdropFilter: 'blur(10px)',
                  borderRadius: 2,
                  overflow: 'hidden',
                  boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.2)}, 0 0 8px ${alpha(theme.palette.primary.main, 0.2)}`
                }}
              >
                <CardHeader 
                  title="Trade Analytics" 
                  titleTypographyProps={{ 
                  fontFamily: 'Orbitron',
                    fontSize: '1.1rem'
                  }} 
                  sx={{ borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}
                />
                <CardContent sx={{ p: 3 }}>
              <Grid container spacing={3}>
                {/* Long vs Short Performance */}
                <Grid item xs={12} md={6}>
                  <Box sx={{ 
                    bgcolor: alpha(theme.palette.background.paper, 0.5), 
                        p: 3, 
                        borderRadius: 2, 
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between'
                      }}>
                        <Typography variant="h6" sx={{ mb: 3, fontFamily: 'Orbitron' }}>
                      Long vs Short Performance
                    </Typography>
                    
                        <Box sx={{ mb: 4, flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                          <Typography variant="body1" fontWeight="medium">Long Trades: {performanceMetrics.longWinRate}% Win Rate</Typography>
                      <Box sx={{ 
                            height: 12, 
                        bgcolor: alpha(theme.palette.success.main, 0.2), 
                            borderRadius: 6, 
                            mt: 1.5, 
                        overflow: 'hidden' 
                      }}>
                        <Box 
                          sx={{ 
                            height: '100%', 
                            width: `${performanceMetrics.longWinRate}%`, 
                            bgcolor: theme.palette.success.main,
                            transition: 'width 1s ease-in-out'
                          }} 
                        />
                      </Box>
                    </Box>
                    
                        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                          <Typography variant="body1" fontWeight="medium">Short Trades: {performanceMetrics.shortWinRate}% Win Rate</Typography>
                      <Box sx={{ 
                            height: 12, 
                        bgcolor: alpha(theme.palette.error.main, 0.2), 
                            borderRadius: 6, 
                            mt: 1.5, 
                        overflow: 'hidden' 
                      }}>
                        <Box 
                          sx={{ 
                            height: '100%', 
                            width: `${performanceMetrics.shortWinRate}%`, 
                            bgcolor: theme.palette.error.main,
                            transition: 'width 1s ease-in-out'
                          }} 
                        />
                      </Box>
                    </Box>
                  </Box>
                </Grid>
                
                    {/* Win/Loss Analysis */}
                <Grid item xs={12} md={6}>
                  <Box sx={{ 
                    bgcolor: alpha(theme.palette.background.paper, 0.5), 
                        p: 3, 
                        borderRadius: 2, 
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column'
                      }}>
                        <Typography variant="h6" sx={{ mb: 3, fontFamily: 'Orbitron' }}>
                          Win/Loss Analysis
                    </Typography>
                    
                        <Grid container spacing={3} sx={{ flexGrow: 1, alignContent: 'space-around' }}>
                          <Grid item xs={6}>
                            <Typography variant="body2" color="text.secondary">Average Win</Typography>
                            <Typography variant="h5" color="success.main" fontWeight="bold">
                        ${performanceMetrics.averageWin}
                      </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="body2" color="text.secondary">Average Loss</Typography>
                            <Typography variant="h5" color="error.main" fontWeight="bold">
                        ${performanceMetrics.averageLoss}
                      </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="body2" color="text.secondary">Max Drawdown</Typography>
                            <Typography variant="h5" color="error.main" fontWeight="bold">
                              ${performanceMetrics.maxDrawdown}
                      </Typography>
                            <Typography variant="body2" color="text.secondary">
                              ({performanceMetrics.maxDrawdownPercent}%)
                    </Typography>
                </Grid>
                          <Grid item xs={6}>
                            <Typography variant="body2" color="text.secondary">Sharpe Ratio</Typography>
                            <Typography variant="h5" fontWeight="bold">
                              {performanceMetrics.sharpeRatio}
                    </Typography>
                          </Grid>
                        </Grid>
                              </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            )}
            
            {/* Trade List Tab */}
            {activeTab === 2 && (
              <Card 
                                  sx={{ 
                  minHeight: '600px',
                  backgroundColor: alpha(theme.palette.background.paper, 0.7),
                  backdropFilter: 'blur(10px)',
                  borderRadius: 2,
                  overflow: 'hidden',
                  boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.2)}, 0 0 8px ${alpha(theme.palette.primary.main, 0.2)}`
                }}
              >
                <CardHeader 
                  title="Trade List" 
                  titleTypographyProps={{ 
                    fontFamily: 'Orbitron',
                    fontSize: '1.1rem'
                  }} 
                  sx={{ borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}
                />
                <CardContent sx={{ p: 0 }}>
                  <TableContainer sx={{ height: 550 }}>
                    <Table stickyHeader size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Symbol</TableCell>
                          <TableCell>Direction</TableCell>
                          <TableCell>Entry Date</TableCell>
                          <TableCell>Exit Date</TableCell>
                          <TableCell align="right">Entry Price</TableCell>
                          <TableCell align="right">Exit Price</TableCell>
                          <TableCell align="right">Quantity</TableCell>
                          <TableCell align="right">Profit/Loss</TableCell>
                          <TableCell>Outcome</TableCell>
                          <TableCell>Exit Reason</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {backtestResults.map((trade, index) => (
                          <TableRow key={index} 
                            sx={{ 
                              bgcolor: trade.trade_outcome === 'win' 
                                ? alpha(theme.palette.success.main, 0.1) 
                                : alpha(theme.palette.error.main, 0.1) 
                            }}
                          >
                            <TableCell>{trade.symbol}</TableCell>
                            <TableCell>
                              {trade.direction === 'long' ? 'Long' : 'Short'}
                            </TableCell>
                            <TableCell>{trade.entry_date}</TableCell>
                            <TableCell>{trade.exit_date}</TableCell>
                            <TableCell align="right">${trade.entry_price}</TableCell>
                            <TableCell align="right">${trade.exit_price}</TableCell>
                            <TableCell align="right">{trade.quantity}</TableCell>
                            <TableCell align="right" 
                              sx={{ 
                                color: parseFloat(trade.profit) >= 0 
                                  ? theme.palette.success.main 
                                  : theme.palette.error.main,
                                fontWeight: 'bold'
                              }}
                            >
                              ${parseFloat(trade.profit).toFixed(2)}
                            </TableCell>
                            <TableCell>
                              <Box 
                                sx={{ 
                                  bgcolor: trade.trade_outcome === 'win' 
                                    ? alpha(theme.palette.success.main, 0.2) 
                                    : alpha(theme.palette.error.main, 0.2),
                                  color: trade.trade_outcome === 'win' 
                                    ? theme.palette.success.main 
                                    : theme.palette.error.main,
                                  py: 0.5,
                                  px: 1,
                                  borderRadius: 1,
                                  display: 'inline-block',
                                  fontSize: '0.75rem',
                                  fontWeight: 'bold'
                                }}
                              >
                                {trade.trade_outcome === 'win' ? 'WIN' : 'LOSS'}
                              </Box>
                            </TableCell>
                            <TableCell>{trade.exit_reason}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            )}
            
            {/* Backtest Settings Tab */}
            {activeTab === 3 && (
              <Card 
                                  sx={{ 
                  minHeight: '600px',
                  backgroundColor: alpha(theme.palette.background.paper, 0.7),
                  backdropFilter: 'blur(10px)',
                  borderRadius: 2,
                  overflow: 'hidden',
                  boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.2)}, 0 0 8px ${alpha(theme.palette.primary.main, 0.2)}`
                }}
              >
                <CardHeader 
                  title="Backtest Settings" 
                  titleTypographyProps={{ 
                    fontFamily: 'Orbitron',
                    fontSize: '1.1rem'
                  }} 
                  sx={{ borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}
                />
                <CardContent sx={{ p: 3 }}>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={4}>
                      <Typography variant="h6" sx={{ mb: 3, fontFamily: 'Orbitron' }}>Data Configuration</Typography>
                      
                      <Box sx={{ mb: 4 }}>
                        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                          Data Source
                        </Typography>
                        <Typography variant="body1">
                          {dataSource === 'api' ? 'Live API Data' : dataSource === 'csv' ? 'CSV File Data' : 'Sample Demo Data'}
                        </Typography>
                              </Box>
                      
                      <Box sx={{ mb: 4 }}>
                        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                          Time Period
                        </Typography>
                        <TextField
                          select
                          value={timeframe}
                          onChange={handleTimeframeChange}
                          fullWidth
                          size="small"
                          sx={{ mb: 2 }}
                        >
                          <MenuItem value="all">All Data</MenuItem>
                          <MenuItem value="1m">Last Month</MenuItem>
                          <MenuItem value="3m">Last 3 Months</MenuItem>
                          <MenuItem value="6m">Last 6 Months</MenuItem>
                          <MenuItem value="1y">Last Year</MenuItem>
                        </TextField>
                            </Box>
                      
                      <Button
                        variant="contained"
                        color="primary"
                        startIcon={<PlayArrow />}
                        fullWidth
                        onClick={handleRefresh}
                        sx={{ mt: 2 }}
                      >
                        Run Backtest
                      </Button>
                      </Grid>
                      
                    <Grid item xs={12} md={8}>
                      <Typography variant="h6" sx={{ mb: 3, fontFamily: 'Orbitron' }}>Strategy Configuration</Typography>
                      
                      <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                          <Box sx={{ mb: 3 }}>
                            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                              Capital Settings
                        </Typography>
                            
                            <TextField
                              label="Initial Capital"
                              type="number"
                              defaultValue={10000}
                              fullWidth
                              size="small"
                              sx={{ mb: 2 }}
                            />
                            
                            <TextField
                              label="Position Size (%)"
                              type="number"
                              defaultValue={10}
                              fullWidth
                              size="small"
                            />
                  </Box>
                </Grid>
                
                        <Grid item xs={12} md={6}>
                          <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                              Trade Settings
                    </Typography>
                    
                            <TextField
                              select
                              label="Strategy Type"
                              defaultValue="default"
                              fullWidth
                              size="small"
                              sx={{ mb: 2 }}
                            >
                              <MenuItem value="default">Default Strategy</MenuItem>
                              <MenuItem value="conservative">Conservative</MenuItem>
                              <MenuItem value="aggressive">Aggressive</MenuItem>
                            </TextField>
                            
                            <TextField
                              select
                              label="Slippage Model"
                              defaultValue="fixed"
                              fullWidth
                              size="small"
                            >
                              <MenuItem value="none">No Slippage</MenuItem>
                              <MenuItem value="fixed">Fixed (0.1%)</MenuItem>
                              <MenuItem value="variable">Variable (0.05-0.3%)</MenuItem>
                              <MenuItem value="volume">Volume-Based</MenuItem>
                            </TextField>
                  </Box>
                        </Grid>
                      </Grid>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
      )}
    </Box>
        )}
      </Box>
    </Container>
  );
};

export default Backtest; 