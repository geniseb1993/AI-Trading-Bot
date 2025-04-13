import React, { useMemo } from 'react';
import { 
  Box, 
  Typography, 
  List, 
  ListItem, 
  Divider, 
  Chip, 
  useTheme,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  TrendingUp, 
  TrendingDown, 
  Close, 
  Info 
} from '@mui/icons-material';

/**
 * ActiveTrades component displays a list of active trading positions
 * 
 * @param {Object} props
 * @param {Array} props.trades - Array of trade objects
 * @returns {JSX.Element}
 */
const ActiveTrades = ({ trades }) => {
  const theme = useTheme();
  
  // Process trades data to handle various formats
  const processedTrades = useMemo(() => {
    if (!trades) return [];
    
    // Check if array is already in the expected format
    if (trades.length > 0 && trades[0].side !== undefined) {
      return trades;
    }
    
    // If trades is an array from CSV format
    return trades.map(trade => ({
      id: trade.symbol + '-' + (trade.entry_date || '').replace(/\s+/g, '-'),
      symbol: trade.symbol,
      side: trade.position_type === 'SHORT' ? 'SELL' : 'BUY',
      entryPrice: parseFloat(trade.entry_price),
      currentPrice: parseFloat(trade.current_price),
      quantity: parseFloat(trade.quantity),
      pnl: parseFloat(trade.pnl),
      pnlPercent: parseFloat(trade.pnl_percent),
      openTime: trade.entry_date
    }));
  }, [trades]);
  
  if (!processedTrades || processedTrades.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <Typography>No active trades</Typography>
      </Box>
    );
  }

  // Format datetime
  const formatTime = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return dateString; // Return the original string if parsing fails
    }
  };

  return (
    <List sx={{ 
      width: '100%', 
      maxHeight: '300px', 
      overflow: 'auto',
      '&::-webkit-scrollbar': {
        width: '8px',
      },
      '&::-webkit-scrollbar-thumb': {
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: '4px',
      },
    }}>
      {processedTrades.map((trade, index) => (
        <React.Fragment key={trade.id || index}>
          {index > 0 && <Divider component="li" />}
          <ListItem
            sx={{ 
              py: 2,
              display: 'flex',
              flexDirection: {
                xs: 'column',
                sm: 'row'
              },
              alignItems: {
                xs: 'flex-start',
                sm: 'center'
              },
              columnGap: 2,
            }}
          >
            {/* Symbol and side */}
            <Box sx={{ 
              display: 'flex',
              alignItems: 'center',
              minWidth: '120px',
              mr: {
                xs: 0,
                sm: 2
              },
              mb: {
                xs: 1,
                sm: 0
              }
            }}>
              <Chip 
                label={trade.symbol}
                color="primary"
                size="small"
                sx={{ mr: 1 }}
              />
              <Chip 
                label={trade.side}
                color={trade.side === 'BUY' ? 'success' : 'error'}
                size="small"
                icon={trade.side === 'BUY' ? <TrendingUp /> : <TrendingDown />}
              />
            </Box>
            
            {/* Entry price and current price */}
            <Box sx={{ 
              display: 'flex',
              flexDirection: 'column',
              minWidth: '120px',
              mr: {
                xs: 0,
                sm: 2
              },
              mb: {
                xs: 1,
                sm: 0
              }
            }}>
              <Typography variant="body2" color="text.secondary">
                Entry: ${trade.entryPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </Typography>
              <Typography variant="body2">
                Current: ${trade.currentPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </Typography>
            </Box>
            
            {/* PNL */}
            <Box sx={{ 
              display: 'flex',
              flexDirection: 'column',
              minWidth: '90px',
              mr: 'auto',
              mb: {
                xs: 1,
                sm: 0
              }
            }}>
              <Typography 
                variant="body2" 
                fontWeight="bold"
                color={trade.pnl >= 0 ? 'success.main' : 'error.main'}
              >
                {trade.pnl >= 0 ? '+' : ''}{trade.pnl.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </Typography>
              <Typography 
                variant="body2"
                color={trade.pnlPercent >= 0 ? 'success.main' : 'error.main'}
              >
                {trade.pnlPercent >= 0 ? '+' : ''}{Number(trade.pnlPercent).toFixed(2)}%
              </Typography>
            </Box>
            
            {/* Time and quantity */}
            <Box sx={{ 
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-end',
              minWidth: '120px',
            }}>
              <Typography variant="caption" color="text.secondary">
                {formatTime(trade.openTime)}
              </Typography>
              <Typography variant="body2">
                Qty: {trade.quantity}
              </Typography>
            </Box>
            
            {/* Actions */}
            <Box sx={{ 
              display: 'flex',
              ml: 1
            }}>
              <Tooltip title="Trade Details">
                <IconButton size="small">
                  <Info fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Close Position">
                <IconButton size="small" color="error">
                  <Close fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </ListItem>
        </React.Fragment>
      ))}
    </List>
  );
};

export default ActiveTrades; 