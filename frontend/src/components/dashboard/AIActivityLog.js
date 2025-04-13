import React, { useState, useEffect, useCallback } from 'react';
import { 
  Card, CardHeader, CardContent, Typography, Box, 
  Chip, Grid, Button, FormControl, InputLabel, 
  Select, MenuItem, TextField, IconButton, 
  Dialog, DialogTitle, DialogContent, DialogActions,
  Table, TableBody, TableCell, TableContainer, 
  TableHead, TableRow, Paper, Collapse, Divider
} from '@mui/material';
import { makeStyles } from '@mui/styles';
import RefreshIcon from '@mui/icons-material/Refresh';
import FilterListIcon from '@mui/icons-material/FilterList';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import SearchIcon from '@mui/icons-material/Search';
import ErrorIcon from '@mui/icons-material/Error';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import InfoIcon from '@mui/icons-material/Info';
import WarningIcon from '@mui/icons-material/Warning';
import { format } from 'date-fns';
import { useSnackbar } from 'notistack';
import axios from 'axios';

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
    marginBottom: 20
  },
  filterBar: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: 16,
    flexWrap: 'wrap',
    gap: 8
  },
  formControl: {
    minWidth: 120,
  },
  tableContainer: {
    maxHeight: 600,
    minHeight: 400,
    overflow: 'auto'
  },
  actionChip: {
    marginRight: 4,
    marginBottom: 4
  },
  detailsBox: {
    padding: 16,
    backgroundColor: '#f5f5f5',
    borderRadius: 4,
    marginTop: 8
  },
  iconCell: {
    width: 48
  },
  descriptionCell: {
    minWidth: 300
  },
  chip: {
    height: 24,
  },
  noData: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 32
  },
  entry: {
    borderLeft: '4px solid #4caf50'
  },
  exit: {
    borderLeft: '4px solid #f44336'
  },
  signal: {
    borderLeft: '4px solid #2196f3'
  },
  analysis: {
    borderLeft: '4px solid #9c27b0'
  },
  strategy: {
    borderLeft: '4px solid #ff9800'
  },
  risk: {
    borderLeft: '4px solid #00bcd4'
  },
  system: {
    borderLeft: '4px solid #607d8b'
  },
  backtest: {
    borderLeft: '4px solid #8bc34a'
  },
  error: {
    borderLeft: '4px solid #f44336'
  }
}));

// Row component for expanding details
function LogRow(props) {
  const { row, classes } = props;
  const [open, setOpen] = useState(false);
  
  // Handle null or undefined row data
  if (!row) {
    return null;
  }

  // Get class based on activity type
  const getRowClass = (type) => {
    if (!type) return '';
    
    type = type.toLowerCase();
    if (type.includes('entry')) return classes.entry;
    if (type.includes('exit')) return classes.exit;
    if (type.includes('signal')) return classes.signal;
    if (type.includes('analysis')) return classes.analysis;
    if (type.includes('strategy')) return classes.strategy;
    if (type.includes('risk')) return classes.risk;
    if (type.includes('system')) return classes.system;
    if (type.includes('backtest')) return classes.backtest;
    if (type.includes('error')) return classes.error;
    
    return '';
  };

  // Get icon based on activity type
  const getActivityIcon = (type) => {
    if (!type) return <InfoIcon />;
    
    type = type.toLowerCase();
    if (type.includes('error')) return <ErrorIcon color="error" />;
    if (type.includes('entry') || type.includes('exit')) return <CheckCircleIcon color="primary" />;
    if (type.includes('signal')) return <SearchIcon color="secondary" />;
    if (type.includes('risk')) return <WarningIcon style={{ color: '#ff9800' }} />;
    
    return <InfoIcon color="action" />;
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    try {
      return format(new Date(timestamp), 'MMM dd, yyyy HH:mm:ss');
    } catch (error) {
      console.error('Error formatting timestamp:', error, timestamp);
      return timestamp || 'Unknown';
    }
  };

  // Format JSON for display
  const formatJSON = (json) => {
    if (!json) return 'No details';
    if (typeof json === 'string') {
      try {
        json = JSON.parse(json);
      } catch (e) {
        console.error('Error parsing JSON:', e);
        return json;
      }
    }
    try {
      return JSON.stringify(json, null, 2);
    } catch (e) {
      console.error('Error stringifying JSON:', e);
      return 'Invalid JSON data';
    }
  };

  return (
    <React.Fragment>
      <TableRow className={getRowClass(row.activity_type)}>
        <TableCell className={classes.iconCell}>
          {getActivityIcon(row.activity_type)}
        </TableCell>
        <TableCell>
          <Typography variant="body2" color="textSecondary">
            {formatTimestamp(row.timestamp)}
          </Typography>
        </TableCell>
        <TableCell>
          <Chip 
            size="small" 
            className={classes.chip}
            label={row.activity_type || 'Unknown'} 
            color={row.activity_type?.toLowerCase().includes('error') ? 'error' : 'primary'}
            variant="outlined"
          />
        </TableCell>
        <TableCell className={classes.descriptionCell}>
          <Typography variant="body2">
            {row.description}
          </Typography>
        </TableCell>
        <TableCell>
          {row.symbol && (
            <Chip 
              size="small" 
              className={classes.chip}
              label={row.symbol} 
              variant="outlined"
              color="secondary"
            />
          )}
        </TableCell>
        <TableCell>
          <Chip 
            size="small" 
            className={classes.chip}
            label={row.source || 'Unknown'} 
            variant="outlined"
          />
        </TableCell>
        <TableCell>
          <IconButton
            aria-label="expand row"
            size="small"
            onClick={() => setOpen(!open)}
          >
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={7}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box className={classes.detailsBox} sx={{ margin: 1 }}>
              <Typography variant="h6" gutterBottom component="div">
                Details
              </Typography>
              <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.875rem' }}>
                {formatJSON(row.details)}
              </pre>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </React.Fragment>
  );
}

function AIActivityLog() {
  const classes = useStyles();
  const { enqueueSnackbar } = useSnackbar() || {};
  
  // State variables
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterOpen, setFilterOpen] = useState(false);
  const [activityTypes, setActivityTypes] = useState([]);
  
  // Filter states
  const [filters, setFilters] = useState({
    activity_type: '',
    symbol: '',
    source: '',
    start_time: '',
    end_time: '',
    limit: 50
  });
  
  // Get activity types from API
  const fetchActivityTypes = useCallback(async () => {
    try {
      const response = await axios.get('/api/ai-activity/activity-types');
      if (response?.data?.success === false) {
        console.error('Error response from activity types API:', response.data.error || 'Unknown error');
        return;
      }
      
      if (response?.data?.activity_types) {
        // Convert to array if response is an object
        const types = response.data.activity_types;
        if (typeof types === 'object' && !Array.isArray(types)) {
          // If it's an object of format {TYPE_NAME: "type_value"}, extract the values
          setActivityTypes(Object.values(types));
        } else if (Array.isArray(types)) {
          setActivityTypes(types);
        } else {
          console.error('Unexpected activity types format:', types);
          setActivityTypes([]);
        }
      } else {
        console.warn('Activity types not found in response:', response.data);
        // Provide some default activity types as fallback
        setActivityTypes([
          'TRADE_ENTRY', 
          'TRADE_EXIT', 
          'SIGNAL_GENERATED', 
          'MARKET_ANALYSIS', 
          'STRATEGY_SWITCH',
          'RISK_ADJUSTMENT',
          'SYSTEM_ACTION',
          'BACKTEST',
          'ERROR'
        ]);
      }
    } catch (error) {
      console.error('Error fetching activity types:', error);
      setActivityTypes([]);
    }
  }, []);
  
  // Fetch logs based on current filters
  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      // Build query params
      const params = {};
      if (filters.activity_type) params.type = filters.activity_type;
      if (filters.symbol) params.symbol = filters.symbol;
      if (filters.source) params.source = filters.source;
      if (filters.start_time) params.start_time = filters.start_time;
      if (filters.end_time) params.end_time = filters.end_time;
      if (filters.limit) params.limit = filters.limit;
      
      const response = await axios.get('/api/ai-activity/logs', { params });
      if (response?.data?.success === false) {
        console.error('Error response from logs API:', response.data.error || 'Unknown error');
        setLogs([]);
        return;
      }
      
      if (response?.data?.logs) {
        // Make sure logs is always an array
        const receivedLogs = Array.isArray(response.data.logs) ? response.data.logs : [];
        setLogs(receivedLogs);
      } else {
        console.warn('Received unexpected format from logs API:', response.data);
        setLogs([]);
      }
    } catch (error) {
      console.error('Error fetching AI activity logs:', error);
      if (enqueueSnackbar) {
        enqueueSnackbar('Failed to fetch AI activity logs', { variant: 'error' });
      }
      setLogs([]);
    } finally {
      setLoading(false);
    }
  }, [filters, enqueueSnackbar]);
  
  // Handle filter changes
  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters({
      ...filters,
      [name]: value
    });
  };
  
  // Apply filters
  const applyFilters = () => {
    fetchLogs();
    setFilterOpen(false);
  };
  
  // Reset filters
  const resetFilters = () => {
    setFilters({
      activity_type: '',
      symbol: '',
      source: '',
      start_time: '',
      end_time: '',
      limit: 50
    });
  };
  
  // Initialize component
  useEffect(() => {
    let isMounted = true;
    
    const initializeComponent = async () => {
      try {
        await fetchActivityTypes();
        if (isMounted) {
          await fetchLogs();
        }
      } catch (error) {
        console.error('Error initializing AI Activity Log:', error);
        if (isMounted && enqueueSnackbar) {
          enqueueSnackbar('Error loading AI Activity Log', { variant: 'error' });
        }
      }
    };
    
    initializeComponent();
    
    // Cleanup function to prevent memory leaks
    return () => {
      isMounted = false;
    };
  }, [fetchActivityTypes, fetchLogs]);
  
  return (
    <Box className={classes.root} sx={{ minHeight: '500px' }}>
      <Card>
        <CardHeader 
          title="AI Activity Logs" 
          action={
            <Box>
              <IconButton onClick={() => setFilterOpen(true)}>
                <FilterListIcon />
              </IconButton>
              <IconButton onClick={fetchLogs} disabled={loading}>
                <RefreshIcon />
              </IconButton>
            </Box>
          }
        />
        <Divider />
        <CardContent>
          {loading ? (
            <Box className={classes.noData}>
              <Typography variant="body1">Loading activity logs...</Typography>
            </Box>
          ) : logs.length === 0 ? (
            <Box className={classes.noData}>
              <Typography variant="body1">No activity logs found</Typography>
              <Button 
                variant="outlined" 
                color="primary" 
                onClick={fetchLogs} 
                style={{ marginTop: 16 }}
              >
                Refresh
              </Button>
            </Box>
          ) : (
            <TableContainer component={Paper} className={classes.tableContainer}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell></TableCell>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Symbol</TableCell>
                    <TableCell>Source</TableCell>
                    <TableCell>Details</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(logs || []).map((log) => (
                    <LogRow key={log?.id || Math.random().toString(36).substring(7)} row={log} classes={classes} />
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
      
      {/* Filter Dialog */}
      <Dialog open={filterOpen} onClose={() => setFilterOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Filter Activity Logs</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth className={classes.formControl}>
                <InputLabel>Activity Type</InputLabel>
                <Select
                  name="activity_type"
                  value={filters.activity_type}
                  onChange={handleFilterChange}
                >
                  <MenuItem value="">All</MenuItem>
                  {Array.isArray(activityTypes) && activityTypes.map((type) => (
                    <MenuItem key={type} value={type}>
                      {type}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Symbol"
                name="symbol"
                value={filters.symbol}
                onChange={handleFilterChange}
                placeholder="e.g. AAPL"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Source"
                name="source"
                value={filters.source}
                onChange={handleFilterChange}
                placeholder="e.g. ai_trader"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Limit"
                name="limit"
                type="number"
                value={filters.limit}
                onChange={handleFilterChange}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Start Time"
                name="start_time"
                type="datetime-local"
                value={filters.start_time}
                onChange={handleFilterChange}
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="End Time"
                name="end_time"
                type="datetime-local"
                value={filters.end_time}
                onChange={handleFilterChange}
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={resetFilters} color="secondary">
            Reset
          </Button>
          <Button onClick={() => setFilterOpen(false)} color="primary">
            Cancel
          </Button>
          <Button onClick={applyFilters} color="primary" variant="contained">
            Apply
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default AIActivityLog; 