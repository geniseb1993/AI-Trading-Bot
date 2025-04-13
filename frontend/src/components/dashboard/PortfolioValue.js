import React, { useMemo } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Divider, 
  useTheme, 
  Paper,
  LinearProgress
} from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';
import { ResponsivePie } from '@nivo/pie';

/**
 * PortfolioValue component displays portfolio summary information
 * 
 * @param {Object} props
 * @param {Object} props.portfolioData - Portfolio data object
 * @returns {JSX.Element}
 */
const PortfolioValue = ({ portfolioData }) => {
  const theme = useTheme();
  
  // Handle data coming from our API vs. mock data
  const processedData = useMemo(() => {
    if (!portfolioData) return null;

    // Check if the data is coming from our CSV structure
    if (portfolioData.portfolio_performance || portfolioData.portfolio_value) {
      // Data is from CSV - let's convert it to the format our component expects
      const performanceData = portfolioData.portfolio_performance || [];
      
      // Get the most recent data point
      const latestData = performanceData.length > 0 
        ? performanceData[performanceData.length - 1] 
        : null;
      
      // Get data from previous day for daily change
      const previousDayData = performanceData.length > 1 
        ? performanceData[performanceData.length - 2] 
        : null;
      
      // Get data from 7 days ago for weekly change
      const weeklyData = performanceData.length > 7 
        ? performanceData[performanceData.length - 8] 
        : null;
      
      if (!latestData) return null;
      
      // Calculate daily change
      const dailyChange = previousDayData 
        ? parseFloat(latestData.portfolio_value) - parseFloat(previousDayData.portfolio_value)
        : 0;
      
      const dailyChangePercent = previousDayData && parseFloat(previousDayData.portfolio_value) !== 0
        ? (dailyChange / parseFloat(previousDayData.portfolio_value) * 100).toFixed(2)
        : 0;
      
      // Calculate weekly change
      const weeklyChange = weeklyData
        ? parseFloat(latestData.portfolio_value) - parseFloat(weeklyData.portfolio_value)
        : 0;
      
      const weeklyChangePercent = weeklyData && parseFloat(weeklyData.portfolio_value) !== 0
        ? (weeklyChange / parseFloat(weeklyData.portfolio_value) * 100).toFixed(2)
        : 0;
      
      // Create simple allocation mock if not provided
      const cashBalance = latestData.cash_balance ? parseFloat(latestData.cash_balance) : 0;
      const equityValue = latestData.equity_value ? parseFloat(latestData.equity_value) : 0;
      const portfolioValue = parseFloat(latestData.portfolio_value);
      
      const allocation = [
        { asset: 'Cash', value: cashBalance, percent: (cashBalance / portfolioValue * 100) },
        { asset: 'Equity', value: equityValue, percent: (equityValue / portfolioValue * 100) }
      ];
      
      return {
        totalValue: portfolioValue,
        dailyChange: dailyChange,
        dailyChangePercent: dailyChangePercent,
        weeklyChange: weeklyChange,
        weeklyChangePercent: weeklyChangePercent,
        allocation: allocation
      };
    }
    
    // Original object structure
    return {
      totalValue: portfolioData.totalValue || portfolioData.total_value || 0,
      dailyChange: portfolioData.dailyChange || portfolioData.daily_change || 0,
      dailyChangePercent: portfolioData.dailyChangePercent || portfolioData.daily_change_percent || 0,
      weeklyChange: portfolioData.weeklyChange || portfolioData.weekly_change || 0,
      weeklyChangePercent: portfolioData.weeklyChangePercent || portfolioData.weekly_change_percent || 0,
      allocation: portfolioData.allocation || [
        { asset: 'Stock', value: 0, percent: 0 },
        { asset: 'Cash', value: 0, percent: 0 }
      ]
    };
  }, [portfolioData]);
  
  if (!processedData) {
    return <Typography>No portfolio data available</Typography>;
  }

  const {
    totalValue,
    dailyChange,
    dailyChangePercent,
    weeklyChange,
    weeklyChangePercent,
    allocation
  } = processedData;

  // Format data for pie chart
  const chartData = allocation.map(item => ({
    id: item.asset,
    label: item.asset,
    value: item.percent,
    color: getAssetColor(item.asset, theme)
  }));

  return (
    <Box sx={{ 
      width: '100%', 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      <Grid container spacing={2} sx={{ flexGrow: 1, width: '100%', m: 0 }}>
      {/* Main portfolio value */}
        <Grid item xs={12} md={6} sx={{ p: { xs: 1, sm: 1.5 }, height: { xs: 'auto', md: '200px' } }}>
          <Box sx={{ 
            height: '100%', 
            display: 'flex', 
            flexDirection: 'column', 
            justifyContent: 'center' 
          }}>
          <Typography variant="h3" component="div" fontWeight="bold">
            ${totalValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            {dailyChange >= 0 ? (
              <TrendingUp color="success" sx={{ mr: 1 }} />
            ) : (
              <TrendingDown color="error" sx={{ mr: 1 }} />
            )}
            
            <Typography 
              variant="body1" 
              color={dailyChange >= 0 ? 'success.main' : 'error.main'}
              fontWeight="bold"
              sx={{ mr: 2 }}
            >
              {dailyChange >= 0 ? '+' : ''}{dailyChange.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ({dailyChange >= 0 ? '+' : ''}{dailyChangePercent}%)
            </Typography>
            
            <Typography variant="body2" color="text.secondary">
              Today
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            {weeklyChange >= 0 ? (
              <TrendingUp color="success" sx={{ mr: 1 }} />
            ) : (
              <TrendingDown color="error" sx={{ mr: 1 }} />
            )}
            
            <Typography 
              variant="body1" 
              color={weeklyChange >= 0 ? 'success.main' : 'error.main'}
              fontWeight="bold"
              sx={{ mr: 2 }}
            >
              {weeklyChange >= 0 ? '+' : ''}{weeklyChange.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ({weeklyChange >= 0 ? '+' : ''}{weeklyChangePercent}%)
            </Typography>
            
            <Typography variant="body2" color="text.secondary">
              This Week
            </Typography>
          </Box>
        </Box>
      </Grid>
      
      {/* Portfolio allocation chart */}
        <Grid item xs={12} md={6} sx={{ p: { xs: 1, sm: 1.5 }, height: { xs: 'auto', md: '200px' } }}>
          <Box sx={{ 
            height: '100%', 
            width: '100%', 
            display: 'flex', 
            alignItems: 'center',
            justifyContent: 'center'
          }}>
          <ResponsivePie
            data={chartData}
            margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
            innerRadius={0.6}
            padAngle={0.5}
            cornerRadius={3}
            activeOuterRadiusOffset={8}
            colors={{ datum: 'data.color' }}
            borderWidth={1}
            borderColor={{ from: 'color', modifiers: [['darker', 0.2]] }}
            enableArcLinkLabels={false}
            arcLabelsSkipAngle={10}
            arcLabelsTextColor={{ from: 'color', modifiers: [['darker', 2]] }}
            theme={{
              tooltip: {
                container: {
                  background: theme.palette.background.paper,
                  color: theme.palette.text.primary,
                  fontSize: 12,
                  borderRadius: 4,
                  boxShadow: '0 4px 10px rgba(0, 0, 0, 0.5)',
                },
              },
            }}
            legends={[]}
          />
        </Box>
      </Grid>
      
      <Grid item xs={12}>
          <Divider sx={{ my: 1.5 }} />
          <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1.5, px: 1 }}>
          Asset Allocation
        </Typography>
      </Grid>
      
      {/* Asset allocation breakdown */}
      {allocation.map((asset) => (
          <Grid item xs={12} sm={6} md={3} key={asset.asset} sx={{ p: { xs: 1, sm: 1.5 } }}>
          <Paper
            elevation={0}
            sx={{
                p: 1.5,
              borderRadius: 2,
              backgroundColor: 'background.paper',
              border: '1px solid',
              borderColor: 'divider',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body1" fontWeight="bold">
                {asset.asset}
              </Typography>
              <Typography variant="body1">
                {asset.percent.toFixed(1)}%
              </Typography>
            </Box>
            
            <LinearProgress
              variant="determinate"
              value={asset.percent}
              sx={{
                mb: 1,
                height: 6,
                borderRadius: 1,
                backgroundColor: `${getAssetColor(asset.asset, theme)}33`,
                '& .MuiLinearProgress-bar': {
                  backgroundColor: getAssetColor(asset.asset, theme),
                },
              }}
            />
            
            <Typography variant="body2">
              ${asset.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </Typography>
          </Paper>
        </Grid>
      ))}
    </Grid>
    </Box>
  );
};

// Helper function to get consistent colors for assets
function getAssetColor(asset, theme) {
  const assetColors = {
    BTC: theme.palette.warning.main,
    ETH: theme.palette.secondary.main,
    BNB: theme.palette.warning.light,
    USDT: theme.palette.success.main,
    SOL: theme.palette.secondary.light,
    XRP: theme.palette.info.main,
    ADA: theme.palette.primary.main,
    DOGE: theme.palette.warning.dark,
    Cash: theme.palette.success.light,
    Equity: theme.palette.primary.main,
    Stock: theme.palette.info.main
  };
  
  return assetColors[asset] || theme.palette.primary.main;
}

export default PortfolioValue; 