import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Paper, 
  Table, 
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  CircularProgress,
  Chip,
  Divider,
  Card,
  CardContent,
  Tabs,
  Tab,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  TrendingUp, 
  TrendingDown, 
  Refresh, 
  Search, 
  MoreVert,
  Star,
  StarBorder
} from '@mui/icons-material';
import axios from 'axios';

const InstitutionalFlow = () => {
  const [flowData, setFlowData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [timeFilter, setTimeFilter] = useState('today');
  const [sectorFilter, setSectorFilter] = useState('all');
  const [favoriteSymbols, setFavoriteSymbols] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  const tabOptions = ['Options Flow', 'Dark Pool', '13F Filings', 'Insider Trading'];
  
  const timeFilters = [
    { value: 'today', label: 'Today' },
    { value: 'yesterday', label: 'Yesterday' },
    { value: 'this_week', label: 'This Week' },
    { value: 'this_month', label: 'This Month' },
  ];
  
  const sectors = [
    { value: 'all', label: 'All Sectors' },
    { value: 'technology', label: 'Technology' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'finance', label: 'Finance' },
    { value: 'consumer', label: 'Consumer' },
    { value: 'energy', label: 'Energy' },
    { value: 'materials', label: 'Materials' },
    { value: 'industrials', label: 'Industrials' },
  ];

  useEffect(() => {
    fetchInstitutionalFlowData();
  }, [tabValue, timeFilter, sectorFilter]);

  const fetchInstitutionalFlowData = async () => {
    setLoading(true);
    try {
      // Try to fetch data from API
      const response = await axios.post('/api/institutional-flow/get-data', {
        type: tabOptions[tabValue].toLowerCase().replace(' ', '-'),
        timeframe: timeFilter,
        sector: sectorFilter
      });
      
      if (response.data && response.data.success && Array.isArray(response.data.data)) {
        setFlowData(response.data.data);
      } else {
        // If API fails, generate mock data
        generateMockData();
      }
    } catch (error) {
      console.error('Error fetching institutional flow data:', error);
      // Generate mock data if API request fails
      generateMockData();
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = () => {
    const mockData = [];
    const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'AMD', 'NFLX', 'JPM'];
    const sectors = ['Technology', 'Healthcare', 'Finance', 'Consumer', 'Energy'];
    const institutions = [
      'BlackRock', 'Vanguard', 'Fidelity', 'State Street', 'JP Morgan', 
      'Citadel', 'Renaissance Technologies', 'Two Sigma', 'AQR Capital', 'Point72'
    ];
    
    for (let i = 0; i < 20; i++) {
      const symbol = symbols[Math.floor(Math.random() * symbols.length)];
      const sector = sectors[Math.floor(Math.random() * sectors.length)];
      const institution = institutions[Math.floor(Math.random() * institutions.length)];
      const direction = Math.random() > 0.5 ? 'buy' : 'sell';
      const date = new Date();
      date.setHours(date.getHours() - Math.floor(Math.random() * 72));
      
      let mockItem = {};
      
      // Generate different data based on tab
      if (tabValue === 0) { // Options Flow
        mockItem = {
          id: i + 1,
          timestamp: date.toISOString(),
          symbol,
          sector,
          institution,
          direction,
          contract_type: Math.random() > 0.5 ? 'call' : 'put',
          strike: (Math.random() * 200 + 50).toFixed(2),
          expiry: (() => {
            const expiry = new Date();
            expiry.setDate(expiry.getDate() + Math.floor(Math.random() * 90 + 1));
            return expiry.toISOString().split('T')[0];
          })(),
          premium: (Math.random() * 1000000 + 50000).toFixed(2),
          volume: Math.floor(Math.random() * 5000 + 100),
          open_interest: Math.floor(Math.random() * 10000 + 500),
          unusual: Math.random() > 0.7,
        };
      } else if (tabValue === 1) { // Dark Pool
        mockItem = {
          id: i + 1,
          timestamp: date.toISOString(),
          symbol,
          sector,
          institution,
          direction,
          price: (Math.random() * 1000 + 10).toFixed(2),
          volume: Math.floor(Math.random() * 1000000 + 10000),
          value: (Math.random() * 10000000 + 100000).toFixed(2),
          vwap: (Math.random() * 1000 + 10).toFixed(2),
          market_share: (Math.random() * 15).toFixed(2) + '%',
        };
      } else if (tabValue === 2) { // 13F Filings
        mockItem = {
          id: i + 1,
          timestamp: date.toISOString(),
          symbol,
          sector,
          institution,
          direction,
          shares: Math.floor(Math.random() * 10000000 + 100000),
          value: (Math.random() * 100000000 + 1000000).toFixed(2),
          change: (Math.random() * 40 - 20).toFixed(2) + '%',
          filing_date: (() => {
            const filing = new Date();
            filing.setDate(filing.getDate() - Math.floor(Math.random() * 90));
            return filing.toISOString().split('T')[0];
          })(),
          quarter: `Q${Math.floor(Math.random() * 4) + 1} ${new Date().getFullYear()}`,
        };
      } else { // Insider Trading
        mockItem = {
          id: i + 1,
          timestamp: date.toISOString(),
          symbol,
          sector,
          insider_name: `${['John', 'Jane', 'Michael', 'Sarah', 'Robert', 'Emily'][Math.floor(Math.random() * 6)]} ${['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis'][Math.floor(Math.random() * 6)]}`,
          position: ['CEO', 'CFO', 'CTO', 'Director', 'VP', 'Board Member'][Math.floor(Math.random() * 6)],
          direction,
          shares: Math.floor(Math.random() * 100000 + 1000),
          value: (Math.random() * 5000000 + 50000).toFixed(2),
          price: (Math.random() * 1000 + 10).toFixed(2),
          filing_date: (() => {
            const filing = new Date();
            filing.setDate(filing.getDate() - Math.floor(Math.random() * 30));
            return filing.toISOString().split('T')[0];
          })(),
        };
      }
      
      mockData.push(mockItem);
    }
    
    setFlowData(mockData);
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleTimeFilterChange = (event) => {
    setTimeFilter(event.target.value);
  };

  const handleSectorFilterChange = (event) => {
    setSectorFilter(event.target.value);
  };

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const toggleFavorite = (symbol) => {
    if (favoriteSymbols.includes(symbol)) {
      setFavoriteSymbols(favoriteSymbols.filter(s => s !== symbol));
    } else {
      setFavoriteSymbols([...favoriteSymbols, symbol]);
    }
  };

  const getFilteredData = () => {
    if (!searchTerm.trim()) return flowData;
    
    return flowData.filter(item => 
      item.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.institution && item.institution.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (item.insider_name && item.insider_name.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  };

  const renderTableHeader = () => {
    switch (tabValue) {
      case 0: // Options Flow
        return (
          <TableRow>
            <TableCell>Time</TableCell>
            <TableCell>Symbol</TableCell>
            <TableCell>Direction</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Strike</TableCell>
            <TableCell>Expiry</TableCell>
            <TableCell align="right">Premium ($)</TableCell>
            <TableCell align="right">Volume</TableCell>
            <TableCell>Institution</TableCell>
            <TableCell align="center">Actions</TableCell>
          </TableRow>
        );
      case 1: // Dark Pool
        return (
          <TableRow>
            <TableCell>Time</TableCell>
            <TableCell>Symbol</TableCell>
            <TableCell>Direction</TableCell>
            <TableCell align="right">Price ($)</TableCell>
            <TableCell align="right">Volume</TableCell>
            <TableCell align="right">Value ($)</TableCell>
            <TableCell>Institution</TableCell>
            <TableCell>Market Share</TableCell>
            <TableCell align="center">Actions</TableCell>
          </TableRow>
        );
      case 2: // 13F Filings
        return (
          <TableRow>
            <TableCell>Filing Date</TableCell>
            <TableCell>Symbol</TableCell>
            <TableCell>Institution</TableCell>
            <TableCell>Quarter</TableCell>
            <TableCell>Direction</TableCell>
            <TableCell align="right">Shares</TableCell>
            <TableCell align="right">Value ($)</TableCell>
            <TableCell>Change</TableCell>
            <TableCell align="center">Actions</TableCell>
          </TableRow>
        );
      case 3: // Insider Trading
        return (
          <TableRow>
            <TableCell>Filing Date</TableCell>
            <TableCell>Symbol</TableCell>
            <TableCell>Insider</TableCell>
            <TableCell>Position</TableCell>
            <TableCell>Direction</TableCell>
            <TableCell align="right">Shares</TableCell>
            <TableCell align="right">Price ($)</TableCell>
            <TableCell align="right">Value ($)</TableCell>
            <TableCell align="center">Actions</TableCell>
          </TableRow>
        );
      default:
        return null;
    }
  };

  const renderTableRow = (item) => {
    switch (tabValue) {
      case 0: // Options Flow
        return (
          <TableRow key={item.id} hover>
            <TableCell>{new Date(item.timestamp).toLocaleTimeString()}</TableCell>
            <TableCell>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {item.symbol}
                {item.unusual && (
                  <Chip 
                    label="UNUSUAL" 
                    color="error" 
                    size="small" 
                    sx={{ ml: 1 }}
                  />
                )}
              </Box>
            </TableCell>
            <TableCell>
              <Chip 
                label={item.direction.toUpperCase()} 
                color={item.direction === 'buy' ? 'success' : 'error'}
                size="small"
                icon={item.direction === 'buy' ? <TrendingUp fontSize="small" /> : <TrendingDown fontSize="small" />}
              />
            </TableCell>
            <TableCell>
              <Chip 
                label={item.contract_type.toUpperCase()} 
                color={item.contract_type === 'call' ? 'primary' : 'secondary'}
                size="small"
              />
            </TableCell>
            <TableCell>${item.strike}</TableCell>
            <TableCell>{item.expiry}</TableCell>
            <TableCell align="right">${Number(item.premium).toLocaleString()}</TableCell>
            <TableCell align="right">{item.volume.toLocaleString()}</TableCell>
            <TableCell>{item.institution}</TableCell>
            <TableCell align="center">
              <IconButton size="small" onClick={() => toggleFavorite(item.symbol)}>
                {favoriteSymbols.includes(item.symbol) ? 
                  <Star fontSize="small" color="warning" /> : 
                  <StarBorder fontSize="small" />
                }
              </IconButton>
            </TableCell>
          </TableRow>
        );
      case 1: // Dark Pool
        return (
          <TableRow key={item.id} hover>
            <TableCell>{new Date(item.timestamp).toLocaleTimeString()}</TableCell>
            <TableCell>{item.symbol}</TableCell>
            <TableCell>
              <Chip 
                label={item.direction.toUpperCase()} 
                color={item.direction === 'buy' ? 'success' : 'error'}
                size="small"
                icon={item.direction === 'buy' ? <TrendingUp fontSize="small" /> : <TrendingDown fontSize="small" />}
              />
            </TableCell>
            <TableCell align="right">${item.price}</TableCell>
            <TableCell align="right">{Number(item.volume).toLocaleString()}</TableCell>
            <TableCell align="right">${Number(item.value).toLocaleString()}</TableCell>
            <TableCell>{item.institution}</TableCell>
            <TableCell>{item.market_share}</TableCell>
            <TableCell align="center">
              <IconButton size="small" onClick={() => toggleFavorite(item.symbol)}>
                {favoriteSymbols.includes(item.symbol) ? 
                  <Star fontSize="small" color="warning" /> : 
                  <StarBorder fontSize="small" />
                }
              </IconButton>
            </TableCell>
          </TableRow>
        );
      case 2: // 13F Filings
        return (
          <TableRow key={item.id} hover>
            <TableCell>{item.filing_date}</TableCell>
            <TableCell>{item.symbol}</TableCell>
            <TableCell>{item.institution}</TableCell>
            <TableCell>{item.quarter}</TableCell>
            <TableCell>
              <Chip 
                label={item.direction.toUpperCase()} 
                color={item.direction === 'buy' ? 'success' : 'error'}
                size="small"
                icon={item.direction === 'buy' ? <TrendingUp fontSize="small" /> : <TrendingDown fontSize="small" />}
              />
            </TableCell>
            <TableCell align="right">{Number(item.shares).toLocaleString()}</TableCell>
            <TableCell align="right">${Number(item.value).toLocaleString()}</TableCell>
            <TableCell>
              <Chip 
                label={item.change} 
                color={parseFloat(item.change) > 0 ? 'success' : 'error'}
                size="small"
              />
            </TableCell>
            <TableCell align="center">
              <IconButton size="small" onClick={() => toggleFavorite(item.symbol)}>
                {favoriteSymbols.includes(item.symbol) ? 
                  <Star fontSize="small" color="warning" /> : 
                  <StarBorder fontSize="small" />
                }
              </IconButton>
            </TableCell>
          </TableRow>
        );
      case 3: // Insider Trading
        return (
          <TableRow key={item.id} hover>
            <TableCell>{item.filing_date}</TableCell>
            <TableCell>{item.symbol}</TableCell>
            <TableCell>{item.insider_name}</TableCell>
            <TableCell>{item.position}</TableCell>
            <TableCell>
              <Chip 
                label={item.direction.toUpperCase()} 
                color={item.direction === 'buy' ? 'success' : 'error'}
                size="small"
                icon={item.direction === 'buy' ? <TrendingUp fontSize="small" /> : <TrendingDown fontSize="small" />}
              />
            </TableCell>
            <TableCell align="right">{Number(item.shares).toLocaleString()}</TableCell>
            <TableCell align="right">${item.price}</TableCell>
            <TableCell align="right">${Number(item.value).toLocaleString()}</TableCell>
            <TableCell align="center">
              <IconButton size="small" onClick={() => toggleFavorite(item.symbol)}>
                {favoriteSymbols.includes(item.symbol) ? 
                  <Star fontSize="small" color="warning" /> : 
                  <StarBorder fontSize="small" />
                }
              </IconButton>
            </TableCell>
          </TableRow>
        );
      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3, minHeight: '100vh' }}>
      <Typography variant="h4" sx={{ mb: 3 }}>Institutional Flow</Typography>
      
      {/* Tabs Navigation */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          {tabOptions.map((tab, index) => (
            <Tab key={index} label={tab} />
          ))}
        </Tabs>
      </Paper>
      
      {/* Filters and Controls */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Time Period</InputLabel>
              <Select
                value={timeFilter}
                label="Time Period"
                onChange={handleTimeFilterChange}
              >
                {timeFilters.map(filter => (
                  <MenuItem key={filter.value} value={filter.value}>{filter.label}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Sector</InputLabel>
              <Select
                value={sectorFilter}
                label="Sector"
                onChange={handleSectorFilterChange}
              >
                {sectors.map(sector => (
                  <MenuItem key={sector.value} value={sector.value}>{sector.label}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={4}>
            <TextField
              fullWidth
              size="small"
              label="Search by Symbol/Institution/Name"
              value={searchTerm}
              onChange={handleSearch}
              InputProps={{
                startAdornment: <Search color="action" sx={{ mr: 1 }} />,
              }}
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<Refresh />}
              onClick={fetchInstitutionalFlowData}
            >
              Refresh
            </Button>
          </Grid>
        </Grid>
      </Paper>
      
      {/* Main Data Table */}
      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer sx={{ maxHeight: 'calc(100vh - 300px)' }}>
            <Table stickyHeader>
              <TableHead>
                {renderTableHeader()}
              </TableHead>
              <TableBody>
                {getFilteredData().length > 0 ? (
                  getFilteredData().map(item => renderTableRow(item))
                ) : (
                  <TableRow>
                    <TableCell colSpan={10} align="center">
                      No data found. Try adjusting your filters or search terms.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Box>
  );
};

export default InstitutionalFlow; 