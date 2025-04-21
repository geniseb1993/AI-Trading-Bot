import React from 'react';
import { Box, Container, Typography, Paper } from '@mui/material';
import DualBotDashboard from '../components/DualBotDashboard';

const DualBotPage = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Dual Bot Trading System
          </Typography>
          <Typography variant="body1" paragraph>
            This dashboard integrates DeepSeek (trade scanning) and ChatGPT (risk assessment) 
            to provide AI-powered trading recommendations and risk management.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            The Dual Bot system scans the market for potential trades, analyzes them for risk,
            and provides a comprehensive view of trading opportunities with risk assessments.
          </Typography>
        </Paper>
        
        <DualBotDashboard />
      </Box>
    </Container>
  );
};

export default DualBotPage; 