import React, { useState, useEffect, useCallback } from 'react';
import { 
  Box, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper, 
  Typography, 
  Chip,
  IconButton,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  useTheme,
  alpha,
  CircularProgress,
  Alert,
  Pagination
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import FilterListIcon from '@mui/icons-material/FilterList';
import LaunchIcon from '@mui/icons-material/Launch';
import axios from 'axios';

// Fallback mock data in case API is not available
const mockFlowData = [
  {
    id: 1,
    symbol: 'AAPL',
    type: 'sweep',
    direction: 'call',
    premium: 1250000,
    strike: 180,
    expiry: '2023-12-15',
    timestamp: '2023-09-28T14:32:50Z',
    sentiment: 'bullish',
    flow_score: 85,
    unusual_score: 92
  },
  {
    id: 2,
    symbol: 'TSLA',
    type: 'block',
    direction: 'put',
    premium: 3200000,
    strike: 240,
    expiry: '2023-11-17',
    timestamp: '2023-09-28T14:30:15Z',
    sentiment: 'bearish',
    flow_score: 78,
    unusual_score: 88
  },
  {
    id: 3,
    symbol: 'SPY',
    type: 'sweep',
    direction: 'call',
    premium: 1800000,
    strike: 440,
    expiry: '2023-10-20',
    timestamp: '2023-09-28T14:28:30Z',
    sentiment: 'bullish',
    flow_score: 72,
    unusual_score: 75
  },
  {
    id: 4,
    symbol: 'QQQ',
    type: 'unusual',
    direction: 'call',
    premium: 950000,
    strike: 380,
    expiry: '2023-11-17',
    timestamp: '2023-09-28T14:25:10Z',
    sentiment: 'bullish',
    flow_score: 81,
    unusual_score: 89
  },
  {
    id: 5,
    symbol: 'MSFT',
    type: 'block',
    direction: 'put',
    premium: 1500000,
    strike: 330,
    expiry: '2023-12-15',
    timestamp: '2023-09-28T14:20:45Z',
    sentiment: 'bearish',
    flow_score: 65,
    unusual_score: 70
  },
  {
    id: 6,
    symbol: 'NVDA',
    type: 'sweep',
    direction: 'call',
    premium: 2100000,
    strike: 450,
    expiry: '2023-10-20',
    timestamp: '2023-09-28T14:15:30Z',
    sentiment: 'bullish',
    flow_score: 92,
    unusual_score: 95
  },
  {
    id: 7,
    symbol: 'META',
    type: 'unusual',
    direction: 'call',
    premium: 1300000,
    strike: 310,
    expiry: '2023-11-17',
    timestamp: '2023-09-28T14:10:20Z',
    sentiment: 'bullish',
    flow_score: 79,
    unusual_score: 85
  },
  {
    id: 8,
    symbol: 'GOOGL',
    type: 'block',
    direction: 'call',
    premium: 1750000,
    strike: 140,
    expiry: '2023-12-15',
    timestamp: '2023-09-28T14:05:15Z',
    sentiment: 'bullish',
    flow_score: 83,
    unusual_score: 80
  }
];

const InstitutionalFlowTable = () => {
  const theme = useTheme();
  const [flowData, setFlowData] = useState([]);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    symbol: '',
    type: '',
    direction: '',
    sentiment: ''
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [rowsPerPage] = useState(10);
  const [isRealData, setIsRealData] = useState(false);
  const [source, setSource] = useState('unknown');

  const fetchFlowData = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/institutional-flow');
      const responseData = await response.json();
      
      console.log("Institutional flow API response:", responseData);
      
      if (responseData.success) {
        // New format - data is nested under data key and has success field
        setFlowData(responseData.data || []);
        setSource(responseData.source || 'unknown');
        setIsRealData(responseData.source !== 'mock');
        setError(null);
      } else {
        // Handle API error
        console.error("API Error:", responseData.error);
        setError(responseData.error || "Failed to fetch institutional flow data");
        setFlowData(mockFlowData);
        setIsRealData(false);
      }
    } catch (err) {
      console.error("Failed to fetch institutional flow data:", err);
      setError("Failed to fetch institutional flow data");
      setFlowData(mockFlowData);
      setIsRealData(false);
    } finally {
      setLoading(false);
    }
  }, [mockFlowData]);

  const fetchFilteredData = useCallback(async (filters) => {
    setLoading(true);
    try {
      const response = await fetch('/api/institutional-flow/get-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(filters)
      });
      
      const responseData = await response.json();
      console.log("Filtered institutional flow API response:", responseData);
      
      if (responseData.success) {
        setFlowData(responseData.data || []);
        setIsRealData(true);
        setError(null);
      } else {
        // Handle API error
        console.error("API Error:", responseData.error);
        setError(responseData.error || "Failed to fetch filtered institutional flow data");
        setFlowData(mockFlowData);
        setIsRealData(false);
      }
    } catch (err) {
      console.error("Failed to fetch filtered institutional flow data:", err);
      setError("Failed to fetch filtered institutional flow data");
      setFlowData(mockFlowData);
      setIsRealData(false);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleFilterChange = (field, value) => {
    setFilters({ ...filters, [field]: value });
  };

  const handleFilterSubmit = (event) => {
    if (event.preventDefault) {
      event.preventDefault();
    }
    
    const filterData = {
      symbols: filters.symbol ? [filters.symbol] : undefined,
      type: filters.type || undefined,
      direction: filters.direction || undefined
    };
    
    console.log("Applying filters:", filterData);
    fetchFilteredData(filterData);
  };

  const resetFilters = () => {
    setFilters({
      symbol: '',
      type: '',
      direction: '',
      sentiment: ''
    });
    fetchFlowData();
  };

  // Effect to apply filters when they change
  useEffect(() => {
    fetchFlowData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const formatPremium = (premium) => {
    const numPremium = parseFloat(premium) || 0;
    if (numPremium >= 1000000) {
      return `$${(numPremium / 1000000).toFixed(2)}M`;
    } else if (numPremium >= 1000) {
      return `$${(numPremium / 1000).toFixed(2)}K`;
    }
    return `$${numPremium}`;
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      console.error('Error formatting date:', e);
      return 'Invalid date';
    }
  };

  // Calculate pagination
  const handlePageChange = (event, newPage) => {
    setPage(newPage);
  };

  const paginatedData = flowData.slice(
    (page - 1) * rowsPerPage,
    page * rowsPerPage
  );

  // Function to safely get string values with fallbacks
  const safeString = (value, fallback = '') => {
    if (value === undefined || value === null) return fallback;
    return String(value);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2, alignItems: 'center' }}>
        <Typography 
          variant="h6" 
          sx={{ 
            fontFamily: 'Orbitron',
            color: theme.palette.primary.main
          }}
        >
          Institutional Flow Data
          {!isRealData && (
            <Chip 
              size="small" 
              label="Demo Data" 
              color="warning"
              sx={{ ml: 2, fontFamily: 'Roboto' }}
            />
          )}
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <IconButton 
            onClick={resetFilters}
            sx={{ 
              color: theme.palette.info.main
            }}
            disabled={loading}
            title="Refresh Data"
          >
            <LaunchIcon />
          </IconButton>
          <IconButton 
            onClick={() => setShowFilters(!showFilters)}
            sx={{ 
              color: showFilters ? theme.palette.primary.main : 'inherit',
              backgroundColor: showFilters ? alpha(theme.palette.primary.main, 0.1) : 'transparent'
            }}
          >
            <FilterListIcon />
          </IconButton>
        </Box>
      </Box>
      
      {showFilters && (
        <Box 
          sx={{ 
            p: 2, 
            mb: 2, 
            borderRadius: 1,
            backgroundColor: alpha(theme.palette.background.paper, 0.5),
            backdropFilter: 'blur(10px)',
            display: 'flex',
            flexWrap: 'wrap',
            gap: 2
          }}
        >
          <TextField
            select
            label="Symbol"
            value={filters.symbol}
            onChange={(e) => handleFilterChange('symbol', e.target.value)}
            size="small"
            sx={{ minWidth: 120 }}
            disabled={loading}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="SPY">SPY</MenuItem>
            <MenuItem value="QQQ">QQQ</MenuItem>
            <MenuItem value="AAPL">AAPL</MenuItem>
            <MenuItem value="TSLA">TSLA</MenuItem>
            <MenuItem value="MSFT">MSFT</MenuItem>
            <MenuItem value="NVDA">NVDA</MenuItem>
            <MenuItem value="META">META</MenuItem>
            <MenuItem value="GOOGL">GOOGL</MenuItem>
          </TextField>
          
          <FormControl size="small" sx={{ minWidth: 120 }} disabled={loading}>
            <InputLabel>Type</InputLabel>
            <Select
              value={filters.type}
              onChange={(e) => handleFilterChange('type', e.target.value)}
              label="Type"
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="sweep">Sweep</MenuItem>
              <MenuItem value="block">Block</MenuItem>
              <MenuItem value="unusual">Unusual</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl size="small" sx={{ minWidth: 120 }} disabled={loading}>
            <InputLabel>Direction</InputLabel>
            <Select
              value={filters.direction}
              onChange={(e) => handleFilterChange('direction', e.target.value)}
              label="Direction"
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="call">Calls</MenuItem>
              <MenuItem value="put">Puts</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl size="small" sx={{ minWidth: 120 }} disabled={loading}>
            <InputLabel>Sentiment</InputLabel>
            <Select
              value={filters.sentiment}
              onChange={(e) => handleFilterChange('sentiment', e.target.value)}
              label="Sentiment"
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="bullish">Bullish</MenuItem>
              <MenuItem value="bearish">Bearish</MenuItem>
            </Select>
          </FormControl>
        </Box>
      )}
      
      <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
        {isRealData ? (
          <Typography variant="body2" color="text.secondary">
            Data source: {source}
          </Typography>
        ) : (
          <Chip 
            label="Demo Data" 
            color="warning" 
            size="small" 
            sx={{ mr: 1 }} 
          />
        )}
        {error && (
          <Typography variant="body2" color="error" sx={{ ml: 1 }}>
            {error}
          </Typography>
        )}
      </Box>
      
      <TableContainer 
        component={Paper}
        sx={{ 
          backgroundColor: alpha(theme.palette.background.paper, 0.7),
          backdropFilter: 'blur(10px)',
          borderRadius: 2,
          overflowX: 'auto',
          minHeight: '400px'
        }}
      >
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <Table sx={{ minWidth: 650 }} aria-label="institutional flow table">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold', fontFamily: 'Orbitron' }}>Symbol</TableCell>
                  <TableCell sx={{ fontWeight: 'bold', fontFamily: 'Orbitron' }}>Type</TableCell>
                  <TableCell sx={{ fontWeight: 'bold', fontFamily: 'Orbitron' }}>Direction</TableCell>
                  <TableCell sx={{ fontWeight: 'bold', fontFamily: 'Orbitron' }}>Premium</TableCell>
                  <TableCell sx={{ fontWeight: 'bold', fontFamily: 'Orbitron' }}>Strike</TableCell>
                  <TableCell sx={{ fontWeight: 'bold', fontFamily: 'Orbitron' }}>Expiry</TableCell>
                  <TableCell sx={{ fontWeight: 'bold', fontFamily: 'Orbitron' }}>Time</TableCell>
                  <TableCell sx={{ fontWeight: 'bold', fontFamily: 'Orbitron' }}>Sentiment</TableCell>
                  <TableCell sx={{ fontWeight: 'bold', fontFamily: 'Orbitron' }}>Score</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedData.length > 0 ? (
                  paginatedData.map((flow) => (
                    <TableRow key={flow.id}>
                      <TableCell sx={{ fontWeight: 'bold' }}>{safeString(flow.symbol)}</TableCell>
                      <TableCell>
                        <Chip 
                          label={safeString(flow.type)} 
                          size="small"
                          sx={{ 
                            backgroundColor: flow.type === 'sweep' 
                              ? alpha(theme.palette.warning.main, 0.2)
                              : flow.type === 'block' 
                                ? alpha(theme.palette.info.main, 0.2)
                                : alpha(theme.palette.secondary.main, 0.2),
                            color: flow.type === 'sweep' 
                              ? theme.palette.warning.main
                              : flow.type === 'block' 
                                ? theme.palette.info.main
                                : theme.palette.secondary.main,
                            fontWeight: 'bold'
                          }} 
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {safeString(flow.direction) === 'call' ? (
                            <TrendingUpIcon fontSize="small" sx={{ color: theme.palette.success.main, mr: 0.5 }} />
                          ) : (
                            <TrendingDownIcon fontSize="small" sx={{ color: theme.palette.error.main, mr: 0.5 }} />
                          )}
                          {safeString(flow.direction)}
                        </Box>
                      </TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>{formatPremium(flow.premium)}</TableCell>
                      <TableCell>${flow.strike || 0}</TableCell>
                      <TableCell>{flow.expiry ? new Date(flow.expiry).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' }) : 'N/A'}</TableCell>
                      <TableCell>{flow.timestamp ? formatDate(flow.timestamp) : 'N/A'}</TableCell>
                      <TableCell>
                        <Chip 
                          label={safeString(flow.sentiment)} 
                          size="small"
                          sx={{ 
                            backgroundColor: safeString(flow.sentiment) === 'bullish' 
                              ? alpha(theme.palette.success.main, 0.2)
                              : alpha(theme.palette.error.main, 0.2),
                            color: safeString(flow.sentiment) === 'bullish' 
                              ? theme.palette.success.main
                              : theme.palette.error.main,
                            fontWeight: 'bold'
                          }} 
                        />
                      </TableCell>
                      <TableCell>
                        <Box 
                          sx={{ 
                            width: 45,
                            height: 45,
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: `conic-gradient(${theme.palette.primary.main} ${flow.unusual_score || 0}%, transparent 0)`,
                            position: 'relative'
                          }}
                        >
                          <Box 
                            sx={{ 
                              width: 35,
                              height: 35,
                              borderRadius: '50%',
                              backgroundColor: alpha(theme.palette.background.paper, 0.8),
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontWeight: 'bold',
                              fontSize: '0.75rem'
                            }}
                          >
                            {flow.unusual_score || 0}
                          </Box>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={9} align="center">
                      <Typography variant="body1" sx={{ py: 3 }}>
                        No results found. Try adjusting your filters.
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </>
        )}
      </TableContainer>
      
      {!loading && flowData.length > rowsPerPage && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <Pagination 
            count={Math.ceil(flowData.length / rowsPerPage)} 
            page={page} 
            onChange={handlePageChange}
            color="primary"
          />
        </Box>
      )}
      
      <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between' }}>
        <Typography variant="caption" sx={{ fontStyle: 'italic', color: 'text.secondary' }}>
          {isRealData ? 'Data source: Unusual Whales API' : 'Using demo data (Unusual Whales API format)'}
        </Typography>
        
        <IconButton 
          size="small" 
          sx={{ color: theme.palette.primary.main }}
          onClick={() => window.open('https://unusualwhales.com/', '_blank')}
        >
          <LaunchIcon fontSize="small" />
        </IconButton>
      </Box>
    </Box>
  );
};

export default InstitutionalFlowTable; 