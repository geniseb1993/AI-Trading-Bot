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
  Pagination,
  Tooltip,
  Button
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import FilterListIcon from '@mui/icons-material/FilterList';
import LaunchIcon from '@mui/icons-material/Launch';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
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
        setIsRealData(responseData.isRealData === true);
        setError(null);
      } else {
        // Handle API error
        console.error("API Error:", responseData.error);
        setError(responseData.error || "Failed to fetch institutional flow data");
        setFlowData(mockFlowData);
        setIsRealData(false);
        setSource('mock');
      }
    } catch (err) {
      console.error("Failed to fetch institutional flow data:", err);
      setError("Failed to fetch institutional flow data");
      setFlowData(mockFlowData);
      setIsRealData(false);
      setSource('mock');
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
        setIsRealData(responseData.isRealData === true);
        setSource(responseData.source || responseData.isRealData ? 'Unusual Whales API' : 'mock');
        setError(null);
      } else {
        // Handle API error
        console.error("API Error:", responseData.error);
        setError(responseData.error || "Failed to fetch filtered institutional flow data");
        setFlowData(mockFlowData);
        setIsRealData(false);
        setSource('mock');
      }
    } catch (err) {
      console.error("Failed to fetch filtered institutional flow data:", err);
      setError("Failed to fetch filtered institutional flow data");
      setFlowData(mockFlowData);
      setIsRealData(false);
      setSource('mock');
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
      {/* Data Source Indicator */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Institutional Flow Data</Typography>
        <Tooltip title={isRealData 
          ? `Real data from ${source}` 
          : "Mock data is being displayed. This is sample data and does not represent real market activity."}>
          <Chip
            icon={<InfoOutlinedIcon />}
            label={isRealData ? "Real Data" : "Sample Data"}
            color={isRealData ? "success" : "warning"}
            variant="outlined"
            size="small"
          />
        </Tooltip>
      </Box>

      {/* Filter controls */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
          <FormControl sx={{ minWidth: 150 }} size="small">
            <InputLabel>Symbol</InputLabel>
            <Select
              value={filters.symbol}
              label="Symbol"
              onChange={(e) => handleFilterChange('symbol', e.target.value)}
            >
              <MenuItem value="">All Symbols</MenuItem>
              {/* Get unique symbols from data */}
              {Array.from(new Set(flowData.map(item => item.symbol))).map((symbol) => (
                <MenuItem key={symbol} value={symbol}>{symbol}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 150 }} size="small">
            <InputLabel>Type</InputLabel>
            <Select
              value={filters.type}
              label="Type"
              onChange={(e) => handleFilterChange('type', e.target.value)}
            >
              <MenuItem value="">All Types</MenuItem>
              <MenuItem value="sweep">Sweep</MenuItem>
              <MenuItem value="block">Block</MenuItem>
              <MenuItem value="unusual">Unusual</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 150 }} size="small">
            <InputLabel>Direction</InputLabel>
            <Select
              value={filters.direction}
              label="Direction"
              onChange={(e) => handleFilterChange('direction', e.target.value)}
            >
              <MenuItem value="">All Directions</MenuItem>
              <MenuItem value="call">Call</MenuItem>
              <MenuItem value="put">Put</MenuItem>
            </Select>
          </FormControl>

          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button 
              variant="contained" 
              size="small" 
              onClick={handleFilterSubmit}
            >
              Apply Filters
            </Button>
            <Button 
              variant="outlined" 
              size="small" 
              onClick={resetFilters}
            >
              Reset
            </Button>
          </Box>
        </Box>
      </Paper>
      
      {/* Main data table */}
      <Paper sx={{ width: '100%', mb: 2 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : (
          <Box>
            <TableContainer sx={{ maxHeight: 500 }}>
              <Table stickyHeader aria-label="institutional flow table">
                <TableHead>
                  <TableRow>
                    <TableCell>Time</TableCell>
                    <TableCell>Symbol</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Direction</TableCell>
                    <TableCell>Strike</TableCell>
                    <TableCell>Expiry</TableCell>
                    <TableCell align="right">Premium ($)</TableCell>
                    <TableCell>Flow Score</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {flowData
                    .slice((page - 1) * rowsPerPage, page * rowsPerPage)
                    .map((row) => (
                      <TableRow 
                        key={row.id}
                        hover
                        sx={{ 
                          backgroundColor: row.unusual_score > 85 
                            ? alpha(theme.palette.warning.light, 0.1)
                            : 'inherit'
                        }}
                      >
                        <TableCell>{formatDate(row.timestamp)}</TableCell>
                        <TableCell>{safeString(row.symbol)}</TableCell>
                        <TableCell>{safeString(row.type)}</TableCell>
                        <TableCell>
                          <Chip 
                            icon={row.direction === 'call' ? <TrendingUpIcon fontSize="small" /> : <TrendingDownIcon fontSize="small" />}
                            label={safeString(row.direction).toUpperCase()}
                            size="small"
                            color={row.direction === 'call' ? 'success' : 'error'}
                          />
                        </TableCell>
                        <TableCell>{safeString(row.strike)}</TableCell>
                        <TableCell>{safeString(row.expiry)}</TableCell>
                        <TableCell align="right">{formatPremium(row.premium)}</TableCell>
                        <TableCell>
                          {row.flow_score && (
                            <Chip 
                              label={safeString(row.flow_score)}
                              size="small"
                              color={row.flow_score > 80 ? 'success' : 'primary'}
                            />
                          )}
                        </TableCell>
                        <TableCell>
                          <IconButton size="small">
                            <LaunchIcon fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  {flowData.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={9} align="center">
                        No data found
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
              <Pagination 
                count={Math.ceil(flowData.length / rowsPerPage)} 
                page={page} 
                onChange={handlePageChange} 
                color="primary" 
              />
            </Box>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default InstitutionalFlowTable; 