import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Tabs, 
  Tab, 
  Card, 
  CardContent, 
  TextField,
  InputAdornment,
  CircularProgress,
  Button,
  useTheme,
  alpha,
  Divider,
  Chip
} from '@mui/material';
import { 
  TrendingUp, 
  TrendingDown, 
  Search, 
  Refresh,
  Sync
} from '@mui/icons-material';
import axios from 'axios';
import { motion } from 'framer-motion';

import TradingSignalItem from '../components/TradingSignalItem';

const Signals = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [buySignals, setBuySignals] = useState([]);
  const [shortSignals, setShortSignals] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchSignals();
  }, []);

  const fetchSignals = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/get-saved-signals');
      if (response.data.success) {
        setBuySignals(response.data.buy_signals);
        setShortSignals(response.data.short_signals);
      }
    } catch (error) {
      console.error('Error fetching signals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchSignals();
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  // Filter signals based on search term
  const filteredBuySignals = buySignals.filter(signal => 
    signal.symbol && signal.symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredShortSignals = shortSignals.filter(signal => 
    signal.symbol && signal.symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box sx={{ pb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography 
          variant="h4" 
          component={motion.h4}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          sx={{ 
            fontWeight: 'bold',
            color: theme.palette.primary.main
          }}
        >
          Trading Signals
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<Refresh />}
          onClick={handleRefresh}
          sx={{ fontFamily: 'Orbitron' }}
        >
          Refresh Signals
        </Button>
      </Box>

      <Card 
        component={motion.div}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        sx={{ 
          mb: 4,
          backgroundColor: alpha(theme.palette.background.paper, 0.7),
          backdropFilter: 'blur(10px)',
        }}
      >
        <Box sx={{ p: 2 }}>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            mb: 2 
          }}>
            <Tabs 
              value={activeTab} 
              onChange={handleTabChange}
              textColor="primary"
              indicatorColor="primary"
              sx={{
                '& .MuiTab-root': {
                  fontFamily: 'Orbitron',
                  fontSize: '0.9rem',
                  letterSpacing: '0.5px',
                  textTransform: 'uppercase',
                  minWidth: 120,
                },
                '& .Mui-selected': {
                  color: theme.palette.primary.main,
                },
                '& .MuiTabs-indicator': {
                  height: 3,
                  borderRadius: '2px 2px 0 0',
                  boxShadow: `0 0 8px ${theme.palette.primary.main}`,
                },
              }}
            >
              <Tab 
                icon={<TrendingUp />} 
                iconPosition="start" 
                label="Buy Signals" 
              />
              <Tab 
                icon={<TrendingDown />} 
                iconPosition="start" 
                label="Short Signals" 
              />
            </Tabs>
            
            <TextField
              placeholder="Search by symbol..."
              size="small"
              value={searchTerm}
              onChange={handleSearchChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search fontSize="small" />
                  </InputAdornment>
                ),
              }}
              sx={{
                width: 200,
                '& .MuiOutlinedInput-root': {
                  borderRadius: '8px',
                  backgroundColor: alpha(theme.palette.background.paper, 0.5),
                },
              }}
            />
          </Box>
          
          <Divider sx={{ mb: 2 }} />
          
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress size={40} sx={{ color: theme.palette.primary.main }} />
            </Box>
          ) : (
            <Box>
              {activeTab === 0 ? (
                filteredBuySignals.length > 0 ? (
                  <Box sx={{ maxHeight: '60vh', overflow: 'auto' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', p: 2, fontWeight: 'bold' }}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Symbol & Date
                      </Typography>
                      <Typography variant="subtitle2" color="text.secondary">
                        Signal Details
                      </Typography>
                    </Box>
                    {filteredBuySignals.map((signal, index) => (
                      <TradingSignalItem 
                        key={index} 
                        signal={signal} 
                        type="buy" 
                      />
                    ))}
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <Chip 
                        label={`${filteredBuySignals.length} Buy Signal${filteredBuySignals.length !== 1 ? 's' : ''}`}
                        icon={<TrendingUp fontSize="small" />}
                        sx={{ 
                          backgroundColor: alpha(theme.palette.success.main, 0.15),
                          color: theme.palette.success.main,
                          fontWeight: 'bold',
                        }}
                      />
                    </Box>
                  </Box>
                ) : (
                  <Box sx={{ textAlign: 'center', p: 4 }}>
                    <Typography variant="h6" color="text.secondary">
                      No buy signals found
                    </Typography>
                  </Box>
                )
              ) : (
                filteredShortSignals.length > 0 ? (
                  <Box sx={{ maxHeight: '60vh', overflow: 'auto' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', p: 2, fontWeight: 'bold' }}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Symbol & Date
                      </Typography>
                      <Typography variant="subtitle2" color="text.secondary">
                        Signal Details
                      </Typography>
                    </Box>
                    {filteredShortSignals.map((signal, index) => (
                      <TradingSignalItem 
                        key={index} 
                        signal={signal} 
                        type="short" 
                      />
                    ))}
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <Chip 
                        label={`${filteredShortSignals.length} Short Signal${filteredShortSignals.length !== 1 ? 's' : ''}`}
                        icon={<TrendingDown fontSize="small" />}
                        sx={{ 
                          backgroundColor: alpha(theme.palette.error.main, 0.15),
                          color: theme.palette.error.main,
                          fontWeight: 'bold',
                        }}
                      />
                    </Box>
                  </Box>
                ) : (
                  <Box sx={{ textAlign: 'center', p: 4 }}>
                    <Typography variant="h6" color="text.secondary">
                      No short signals found
                    </Typography>
                  </Box>
                )
              )}
            </Box>
          )}
        </Box>
      </Card>
      
      {/* Signal Generation Section */}
      <Card 
        component={motion.div}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        sx={{ 
          mb: 2,
          backgroundColor: alpha(theme.palette.background.paper, 0.7),
          backdropFilter: 'blur(10px)',
        }}
      >
        <CardContent>
          <Typography 
            variant="h6" 
            sx={{ 
              mb: 2, 
              fontFamily: 'Orbitron',
              display: 'flex',
              alignItems: 'center',
              gap: 1,
            }}
          >
            <Sync /> Generate New Signals
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <TextField
              label="Symbols (comma separated)"
              placeholder="SPY,QQQ,TSLA"
              defaultValue="SPY,QQQ,TSLA"
              size="small"
              sx={{ minWidth: 250 }}
            />
            
            <TextField
              label="Days to Analyze"
              type="number"
              defaultValue={7}
              size="small"
              sx={{ width: 150 }}
            />
            
            <Button 
              variant="contained" 
              color="secondary"
              sx={{ 
                height: 40,
                fontFamily: 'Orbitron',
                letterSpacing: '0.5px',
              }}
            >
              Generate Signals
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Signals; 