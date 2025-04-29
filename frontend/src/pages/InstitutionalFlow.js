import React, { useEffect, useState, useCallback } from 'react';
import { 
  Box, 
  Typography, 
  Tabs,
  Tab,
  Paper,
  Grid, 
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tooltip
} from '@mui/material';
import { InfoOutlined } from '@mui/icons-material';
import InstitutionalFlowTable from '../components/InstitutionalFlowTable';
import EnhancedInstitutionalFlow from '../components/EnhancedInstitutionalFlow';
import PageWrapper from '../components/PageWrapper';
import { useInstitutionalFlowData } from '../contexts/DataContext';
import { institutionalFlowService } from '../services/api';

const InstitutionalFlow = () => {
  // Get shared state from context
  const { loading, error, setLoading, setError } = useInstitutionalFlowData();
  
  // Local component state
  const [tabValue, setTabValue] = useState(0);
  const [timeFilter, setTimeFilter] = useState('today');
  const [sectorFilter, setSectorFilter] = useState('all');
  const [flowData, setFlowData] = useState([]);
  const [isRealData, setIsRealData] = useState(false);
  const [dataSource, setDataSource] = useState('Mock Data');

  const tabOptions = ['Options Flow', 'Dark Pool', '13F Filings', 'Insider Trading'];
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    fetchInstitutionalFlowData();
  };
  
  const handleTimeFilterChange = (event) => {
    setTimeFilter(event.target.value);
    fetchInstitutionalFlowData();
  };
  
  const handleSectorFilterChange = (event) => {
    setSectorFilter(event.target.value);
    fetchInstitutionalFlowData();
  };

  const fetchInstitutionalFlowData = useCallback(async () => {
    setLoading(true);
    try {
      const tabType = tabOptions[tabValue].toLowerCase().replace(' ', '-');
      
      console.log(`Fetching data for tab: ${tabType}, timeFilter: ${timeFilter}, sectorFilter: ${sectorFilter}`);
      
      // Use different API endpoints based on tab type
      if (tabType === 'options-flow' || tabType === 'dark-pool') {
        // Get data from service
        const response = await institutionalFlowService.getFilteredData({
          type: tabType,
          timeframe: timeFilter,
          sector: sectorFilter
        });
        
        if (response && response.success && Array.isArray(response.data)) {
          setFlowData(response.data);
          setIsRealData(response.isRealData === true);
          setDataSource(response.isRealData ? 'Unusual Whales API' : 'mock');
        } else {
          throw new Error('Invalid response format');
        }
      } else if (tabType === '13f-filings') {
        const response = await institutionalFlowService.getFilteredData({
          type: '13f',
          timeframe: timeFilter
        });
        
        if (response && response.success && Array.isArray(response.data)) {
          setFlowData(response.data);
          setIsRealData(response.isRealData === true);
          setDataSource(response.isRealData ? 'SEC Database' : 'mock');
          } else {
          throw new Error('Invalid response format for 13F filings');
        }
      } else if (tabType === 'insider-trading') {
        const response = await institutionalFlowService.getFilteredData({
          type: 'insider',
          timeframe: timeFilter,
          sector: sectorFilter
        });
        
        if (response && response.success && Array.isArray(response.data)) {
          setFlowData(response.data);
          setIsRealData(response.isRealData === true);
          setDataSource(response.isRealData ? 'SEC Form 4 Data' : 'mock');
          } else {
          throw new Error('Invalid response format for insider trading');
        }
      }
    } catch (err) {
      console.error('Error fetching institutional flow data:', err);
      setError(err.message || 'Failed to fetch institutional flow data');
      setFlowData([]);
      setIsRealData(false);
      setDataSource('Mock Data (Error)');
    } finally {
      setLoading(false);
    }
  }, [tabValue, timeFilter, sectorFilter, setLoading, setError]);

  useEffect(() => {
    fetchInstitutionalFlowData();
  }, [fetchInstitutionalFlowData]);

  return (
    <PageWrapper 
      title="Institutional Flow" 
      domains={['institutionalFlow']}
    >
    <Box sx={{ p: 3, minHeight: '100vh' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Institutional Flow</Typography>
        <Tooltip title={isRealData ? 
          `Real data from ${dataSource}` : 
          "Mock data is being displayed. Add API keys to view real data."}>
          <Chip 
            icon={<InfoOutlined />}
            label={isRealData ? "Real Data" : "Mock Data"} 
            color={isRealData ? "success" : "warning"}
            variant="outlined"
          />
        </Tooltip>
      </Box>
      
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
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Time Filter</InputLabel>
              <Select
                value={timeFilter}
                label="Time Filter"
                onChange={handleTimeFilterChange}
              >
                <MenuItem value="today">Today</MenuItem>
                <MenuItem value="yesterday">Yesterday</MenuItem>
                <MenuItem value="this_week">This Week</MenuItem>
                <MenuItem value="last_week">Last Week</MenuItem>
                <MenuItem value="this_month">This Month</MenuItem>
                <MenuItem value="last_month">Last Month</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Sector</InputLabel>
              <Select
                value={sectorFilter}
                label="Sector"
                onChange={handleSectorFilterChange}
              >
                <MenuItem value="all">All Sectors</MenuItem>
                <MenuItem value="technology">Technology</MenuItem>
                <MenuItem value="healthcare">Healthcare</MenuItem>
                <MenuItem value="financials">Financials</MenuItem>
                <MenuItem value="consumer">Consumer</MenuItem>
                <MenuItem value="communications">Communications</MenuItem>
                <MenuItem value="industrials">Industrials</MenuItem>
                <MenuItem value="energy">Energy</MenuItem>
                <MenuItem value="utilities">Utilities</MenuItem>
                <MenuItem value="materials">Materials</MenuItem>
                <MenuItem value="real_estate">Real Estate</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      
        {/* Main Content */}
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
            <Typography>Loading institutional flow data...</Typography>
          </Box>
        ) : error ? (
          <Box sx={{ p: 3, bgcolor: 'error.light', borderRadius: 1 }}>
            <Typography color="error">{error}</Typography>
          </Box>
        ) : (
          <>
            {/* Options Flow Table */}
            {tabValue === 0 && (
              <InstitutionalFlowTable 
                data={flowData} 
                isRealData={isRealData} 
                source={dataSource}
                type="options"
              />
            )}
            
            {/* Dark Pool Table */}
            {tabValue === 1 && (
              <InstitutionalFlowTable 
                data={flowData} 
                isRealData={isRealData} 
                source={dataSource}
                type="darkpool"
              />
            )}
            
            {/* 13F Filings Table */}
            {tabValue === 2 && (
              <InstitutionalFlowTable 
                data={flowData} 
                isRealData={isRealData} 
                source={dataSource}
                type="13f"
              />
            )}
            
            {/* Insider Trading Table */}
            {tabValue === 3 && (
              <InstitutionalFlowTable 
                data={flowData} 
                isRealData={isRealData} 
                source={dataSource}
                type="insider"
              />
            )}
            
            {/* Advanced Analysis Section (shown below tables for all tabs) */}
            <Box sx={{ mt: 4 }}>
              <Typography variant="h5" gutterBottom>
                Enhanced Institutional Flow Analysis
              </Typography>
              <EnhancedInstitutionalFlow />
            </Box>
          </>
        )}
    </Box>
    </PageWrapper>
  );
};

export default InstitutionalFlow; 