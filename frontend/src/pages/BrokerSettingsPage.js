import React from 'react';
import { Box, Typography, Container } from '@mui/material';
import BrokerSettings from '../components/BrokerSettings';

const BrokerSettingsPage = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Broker Integration
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Configure and manage broker connections for trading operations
        </Typography>
        
        <BrokerSettings />
      </Box>
    </Container>
  );
};

export default BrokerSettingsPage; 