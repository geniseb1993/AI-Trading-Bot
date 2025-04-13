import React, { useState, useEffect } from 'react';
import { Box, Card, CardContent, Typography, LinearProgress, Chip, Grid } from '@mui/material';
import { alpha, styled } from '@mui/material/styles';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import BlockIcon from '@mui/icons-material/Block';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import TimerIcon from '@mui/icons-material/Timer';

const StyledChip = styled(Chip)(({ theme, color }) => ({
  fontWeight: 'bold',
  backgroundColor: alpha(theme.palette[color].main, 0.2),
  color: theme.palette[color].main,
  '& .MuiChip-icon': {
    color: theme.palette[color].main,
  }
}));

const CooldownTimer = ({ cooldownStatus, onRefresh }) => {
  const [remainingTime, setRemainingTime] = useState(0);
  const [nextTradeTime, setNextTradeTime] = useState(null);
  
  // Update timer every second
  useEffect(() => {
    if (!cooldownStatus) return;
    
    setRemainingTime(cooldownStatus.cooldown_remaining_minutes || 0);
    
    if (cooldownStatus.next_available_trade_time) {
      setNextTradeTime(new Date(cooldownStatus.next_available_trade_time));
    } else {
      setNextTradeTime(null);
    }
    
    const timerInterval = setInterval(() => {
      setRemainingTime(prev => {
        if (prev <= 0) {
          clearInterval(timerInterval);
          if (onRefresh) onRefresh();
          return 0;
        }
        return Math.max(0, prev - (1/60)); // Decrease by 1 second converted to minutes
      });
    }, 1000);
    
    return () => clearInterval(timerInterval);
  }, [cooldownStatus, onRefresh]);

  if (!cooldownStatus) {
    return (
      <Card>
        <CardContent>
          <Typography>Loading cooldown status...</Typography>
        </CardContent>
      </Card>
    );
  }

  const progressValue = cooldownStatus.cooldown_minutes > 0 
    ? 100 - (remainingTime / cooldownStatus.cooldown_minutes * 100) 
    : 100;
    
  const getCooldownStatusChip = () => {
    if (!cooldownStatus.cooldown_enabled) {
      return (
        <StyledChip 
          icon={<BlockIcon />} 
          label="Cooldown Disabled" 
          color="info"
        />
      );
    }
    
    if (cooldownStatus.cooldown_active) {
      return (
        <StyledChip 
          icon={<TimerIcon />} 
          label="Cooldown Active" 
          color="warning"
        />
      );
    }
    
    return (
      <StyledChip 
        icon={<CheckCircleIcon />} 
        label="Ready to Trade" 
        color="success"
      />
    );
  };

  return (
    <Card>
      <CardContent>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                Trade Cooldown Timer
              </Typography>
              {getCooldownStatusChip()}
            </Box>
            
            {cooldownStatus.cooldown_enabled && (
              <>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">
                      {remainingTime > 0 
                        ? `Next trade available in: ${Math.floor(remainingTime)}m ${Math.round((remainingTime % 1) * 60)}s` 
                        : "Trade available now"}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {nextTradeTime && remainingTime > 0 
                        ? `at ${nextTradeTime.toLocaleTimeString()}` 
                        : ""}
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={progressValue} 
                    color={progressValue < 50 ? "warning" : "success"}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
              
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Box sx={{ 
                      bgcolor: alpha('#1976d2', 0.1), 
                      p: 1.5, 
                      borderRadius: 1,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center'
                    }}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Hourly Trades
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                          {cooldownStatus.hourly_trade_count}
                        </Typography>
                        <Typography variant="body2" sx={{ mx: 0.5 }}>
                          /
                        </Typography>
                        <Typography variant="body1">
                          {cooldownStatus.max_trades_per_hour}
                        </Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={(cooldownStatus.hourly_trade_count / cooldownStatus.max_trades_per_hour) * 100} 
                        color="primary"
                        sx={{ height: 6, borderRadius: 3, width: '100%', mt: 1 }}
                      />
                    </Box>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Box sx={{ 
                      bgcolor: alpha('#9c27b0', 0.1), 
                      p: 1.5, 
                      borderRadius: 1,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center'
                    }}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Daily Trades
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                          {cooldownStatus.daily_trade_count}
                        </Typography>
                        <Typography variant="body2" sx={{ mx: 0.5 }}>
                          /
                        </Typography>
                        <Typography variant="body1">
                          {cooldownStatus.max_trades_per_day}
                        </Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={(cooldownStatus.daily_trade_count / cooldownStatus.max_trades_per_day) * 100} 
                        color="secondary"
                        sx={{ height: 6, borderRadius: 3, width: '100%', mt: 1 }}
                      />
                    </Box>
                  </Grid>
                </Grid>
              </>
            )}
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default CooldownTimer; 