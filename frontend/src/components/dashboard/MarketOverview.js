import React, { useMemo } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Paper, 
  Divider, 
  Chip,
  List,
  ListItem,
  ListItemText,
  useTheme,
  alpha,
  LinearProgress
} from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';

/**
 * MarketOverview component displays market metrics, top gainers, and top losers
 * 
 * @param {Object} props
 * @param {Object} props.marketData - Market data object
 * @returns {JSX.Element}
 */
const MarketOverview = ({ marketData }) => {
  const theme = useTheme();
  
  // Process the market data to handle both formats (original and CSV)
  const processedData = useMemo(() => {
    if (!marketData) return null;
    
    // Check if we have market_data from CSV format
    if (marketData.market_data && Array.isArray(marketData.market_data)) {
      const marketItems = marketData.market_data;
      
      // Sort by daily change to get gainers and losers
      const sortedByChange = [...marketItems].sort((a, b) => 
        parseFloat(b.daily_change_percent) - parseFloat(a.daily_change_percent)
      );
      
      const topGainers = sortedByChange
        .filter(item => parseFloat(item.daily_change_percent) > 0)
        .slice(0, 3)
        .map(item => ({
          symbol: item.symbol,
          price: parseFloat(item.price),
          change: parseFloat(item.daily_change_percent)
        }));
        
      const topLosers = sortedByChange
        .filter(item => parseFloat(item.daily_change_percent) < 0)
        .reverse()
        .slice(0, 3)
        .map(item => ({
          symbol: item.symbol,
          price: parseFloat(item.price),
          change: parseFloat(item.daily_change_percent)
        }));
        
      // Calculate rough market metrics
      const btcItem = marketItems.find(item => item.symbol === 'BTC-USD');
      const totalMarketCap = marketItems.reduce((sum, item) => {
        const marketCap = parseFloat(item.market_cap);
        return sum + (isNaN(marketCap) ? 0 : marketCap);
      }, 0);
      
      // Avoid division by zero
      const calculatedBtcDominance = btcItem && totalMarketCap > 0
        ? (parseFloat(btcItem.market_cap || 0) / totalMarketCap * 100)
        : 45.5;
      
      // Convert to trillions, ensure it's a valid number
      const calculatedMarketCap = totalMarketCap > 0
        ? (totalMarketCap / 1000000000000)
        : 2.34; // Default fallback
      
      return {
        topGainers: topGainers || [],
        topLosers: topLosers || [],
        btcDominance: calculatedBtcDominance,
        globalMarketCap: calculatedMarketCap,
        fear_greed_index: 55 // Default value
      };
    }
    
    // Original format
    return marketData;
  }, [marketData]);
  
  if (!processedData) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <Typography>No market data available</Typography>
      </Box>
    );
  }

  const { topGainers = [], topLosers = [], btcDominance = 0, globalMarketCap = 0, fear_greed_index = 50 } = processedData;

  // Get sentiment status based on fear & greed index
  const getSentimentStatus = (index) => {
    const safeIndex = typeof index === 'number' ? index : 50;
    if (safeIndex <= 20) return { label: 'Extreme Fear', color: 'error.dark' };
    if (safeIndex <= 40) return { label: 'Fear', color: 'error.main' };
    if (safeIndex <= 60) return { label: 'Neutral', color: 'warning.main' };
    if (safeIndex <= 80) return { label: 'Greed', color: 'success.main' };
    return { label: 'Extreme Greed', color: 'success.dark' };
  };

  const sentiment = getSentimentStatus(fear_greed_index);

  return (
    <Grid container spacing={3}>
      {/* Market metrics */}
      <Grid item xs={12}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
          <Paper
            elevation={0}
            sx={{
              p: 2,
              borderRadius: 2,
              backgroundColor: 'background.paper',
              border: '1px solid',
              borderColor: 'divider',
              flexGrow: 1,
              minWidth: '120px'
            }}
          >
            <Typography variant="body2" color="text.secondary">
              Global Market Cap
            </Typography>
            <Typography variant="h6" fontWeight="bold">
              ${(typeof globalMarketCap === 'number' && !isNaN(globalMarketCap) ? globalMarketCap.toFixed(2) : '0.00')}T
            </Typography>
          </Paper>

          <Paper
            elevation={0}
            sx={{
              p: 2,
              borderRadius: 2,
              backgroundColor: 'background.paper',
              border: '1px solid',
              borderColor: 'divider',
              flexGrow: 1,
              minWidth: '120px'
            }}
          >
            <Typography variant="body2" color="text.secondary">
              BTC Dominance
            </Typography>
            <Typography variant="h6" fontWeight="bold">
              {(typeof btcDominance === 'number' && !isNaN(btcDominance) ? btcDominance.toFixed(1) : '0.0')}%
            </Typography>
          </Paper>

          <Paper
            elevation={0}
            sx={{
              p: 2,
              borderRadius: 2,
              backgroundColor: 'background.paper',
              border: '1px solid',
              borderColor: 'divider',
              flexGrow: 1,
              minWidth: '120px'
            }}
          >
            <Typography variant="body2" color="text.secondary">
              Fear & Greed Index
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="h6" fontWeight="bold" sx={{ mr: 1 }}>
                {typeof fear_greed_index === 'number' ? fear_greed_index : 50}
              </Typography>
              <Chip 
                label={sentiment.label} 
                size="small"
                sx={{ 
                  backgroundColor: alpha(theme.palette[sentiment.color.split('.')[0]][sentiment.color.split('.')[1] || 'main'], 0.2),
                  color: sentiment.color
                }}
              />
            </Box>
          </Paper>
        </Box>
      </Grid>

      {/* Top gainers and losers */}
      <Grid item xs={12} sm={6}>
        <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1, display: 'flex', alignItems: 'center' }}>
          <TrendingUp color="success" sx={{ mr: 1 }} />
          Top Gainers
        </Typography>
        <List>
          {topGainers && topGainers.length > 0 ? (
            topGainers.map((asset, index) => (
              <ListItem
                key={asset.symbol}
                dense
                sx={{ 
                  py: 1,
                  borderBottom: index < topGainers.length - 1 ? '1px solid' : 'none',
                  borderColor: 'divider'
                }}
              >
                <ListItemText
                  primary={asset.symbol}
                  secondary={`$${asset.price ? asset.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00'}`}
                  primaryTypographyProps={{ fontWeight: 'medium' }}
                />
                <Typography 
                  variant="body2" 
                  fontWeight="bold"
                  color="success.main"
                >
                  +{(typeof asset.change === 'number' && !isNaN(asset.change) ? asset.change.toFixed(1) : '0.0')}%
                </Typography>
              </ListItem>
            ))
          ) : (
            <ListItem dense>
              <ListItemText primary="No gainers data available" />
            </ListItem>
          )}
        </List>
      </Grid>

      <Grid item xs={12} sm={6}>
        <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1, display: 'flex', alignItems: 'center' }}>
          <TrendingDown color="error" sx={{ mr: 1 }} />
          Top Losers
        </Typography>
        <List>
          {topLosers && topLosers.length > 0 ? (
            topLosers.map((asset, index) => (
              <ListItem
                key={asset.symbol}
                dense
                sx={{ 
                  py: 1,
                  borderBottom: index < topLosers.length - 1 ? '1px solid' : 'none',
                  borderColor: 'divider'
                }}
              >
                <ListItemText
                  primary={asset.symbol}
                  secondary={`$${asset.price ? asset.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00'}`}
                  primaryTypographyProps={{ fontWeight: 'medium' }}
                />
                <Typography 
                  variant="body2" 
                  fontWeight="bold"
                  color="error.main"
                >
                  {(typeof asset.change === 'number' && !isNaN(asset.change) ? asset.change.toFixed(1) : '0.0')}%
                </Typography>
              </ListItem>
            ))
          ) : (
            <ListItem dense>
              <ListItemText primary="No losers data available" />
            </ListItem>
          )}
        </List>
      </Grid>

      {/* Market sentiment indicator */}
      <Grid item xs={12}>
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Market Sentiment
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', position: 'relative' }}>
            <Box 
              sx={{ 
                width: '100%', 
                height: '20px', 
                borderRadius: '10px', 
                background: `linear-gradient(90deg, ${theme.palette.error.dark} 0%, ${theme.palette.error.main} 20%, ${theme.palette.warning.main} 50%, ${theme.palette.success.main} 80%, ${theme.palette.success.dark} 100%)`,
                position: 'relative',
                '&::after': {
                  content: '""',
                  position: 'absolute',
                  top: '0',
                  width: '4px',
                  height: '100%',
                  backgroundColor: '#fff',
                  border: '2px solid #000',
                  borderRadius: '4px',
                  left: `${typeof fear_greed_index === 'number' ? Math.min(Math.max(fear_greed_index, 0), 100) : 50}%`,
                  transform: 'translateX(-50%)',
                  zIndex: 1
                }
              }} 
            />
            <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', mt: 1 }}>
              <Typography variant="caption">Extreme Fear</Typography>
              <Typography variant="caption">Fear</Typography>
              <Typography variant="caption">Neutral</Typography>
              <Typography variant="caption">Greed</Typography>
              <Typography variant="caption">Extreme Greed</Typography>
            </Box>
          </Box>
        </Box>
      </Grid>
    </Grid>
  );
};

export default MarketOverview; 