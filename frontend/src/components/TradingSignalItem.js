import React from 'react';
import { Box, Typography, Chip, useTheme, alpha } from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';

const TradingSignalItem = ({ signal, type }) => {
  const theme = useTheme();
  const isBuy = type === 'buy';
  
  // Format date if it exists
  const formattedDate = signal.date 
    ? new Date(signal.date).toLocaleDateString() 
    : 'N/A';

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        p: 1.5,
        borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        '&:hover': {
          backgroundColor: alpha(theme.palette.action.hover, 0.1),
        },
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <Box
          sx={{
            width: 35,
            height: 35,
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: isBuy 
              ? alpha(theme.palette.success.main, 0.15) 
              : alpha(theme.palette.error.main, 0.15),
            color: isBuy ? theme.palette.success.main : theme.palette.error.main,
            mr: 2,
          }}
        >
          {isBuy ? <TrendingUp fontSize="small" /> : <TrendingDown fontSize="small" />}
        </Box>
        <Box>
          <Typography variant="subtitle1" fontWeight="bold">
            {signal.symbol}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {formattedDate}
          </Typography>
        </Box>
      </Box>
      
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        {signal.signal_score && (
          <Chip
            label={`Score: ${parseFloat(signal.signal_score).toFixed(2)}`}
            size="small"
            sx={{
              backgroundColor: isBuy 
                ? alpha(theme.palette.success.main, 0.15) 
                : alpha(theme.palette.error.main, 0.15),
              color: isBuy ? theme.palette.success.main : theme.palette.error.main,
              fontWeight: 'bold',
              borderRadius: '4px',
              mr: 1,
            }}
          />
        )}
        
        <Chip
          label={isBuy ? 'BUY' : 'SHORT'}
          size="small"
          sx={{
            backgroundColor: isBuy ? theme.palette.success.main : theme.palette.error.main,
            color: '#fff',
            fontWeight: 'bold',
            fontFamily: 'Orbitron',
            letterSpacing: '1px',
            fontSize: '0.7rem',
            borderRadius: '4px',
          }}
        />
      </Box>
    </Box>
  );
};

export default TradingSignalItem; 