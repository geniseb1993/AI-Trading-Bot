import React, { useState, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Tooltip,
  Grid,
  Card,
  CardContent,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField
} from '@mui/material';
import {
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  FilterList as FilterListIcon
} from '@mui/icons-material';
import { useNotification, NotificationPriority, NotificationGroup } from '../contexts/NotificationContext';
import { formatDistanceToNow, format } from 'date-fns';

const priorityColors = {
  [NotificationPriority.HIGH]: 'error',
  [NotificationPriority.MEDIUM]: 'warning',
  [NotificationPriority.LOW]: 'info'
};

const groupIcons = {
  [NotificationGroup.TRADE]: <CircleIcon />,
  [NotificationGroup.SYSTEM]: <InfoIcon />,
  [NotificationGroup.ALERT]: <WarningIcon />,
  [NotificationGroup.ERROR]: <ErrorIcon />
};

const NotificationHistory = () => {
  const { notifications, removeNotification } = useNotification();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [filters, setFilters] = useState({
    group: '',
    priority: '',
    dateRange: {
      start: '',
      end: ''
    }
  });

  const filteredNotifications = useMemo(() => {
    return notifications.filter(notification => {
      if (filters.group && notification.group !== filters.group) return false;
      if (filters.priority && notification.priority !== filters.priority) return false;
      
      const notificationDate = new Date(notification.timestamp);
      if (filters.dateRange.start && notificationDate < new Date(filters.dateRange.start)) return false;
      if (filters.dateRange.end && notificationDate > new Date(filters.dateRange.end)) return false;
      
      return true;
    });
  }, [notifications, filters]);

  const analytics = useMemo(() => {
    const total = notifications.length;
    const unread = notifications.filter(n => !n.read).length;
    const byPriority = Object.values(NotificationPriority).reduce((acc, priority) => {
      acc[priority] = notifications.filter(n => n.priority === priority).length;
      return acc;
    }, {});
    const byGroup = Object.values(NotificationGroup).reduce((acc, group) => {
      acc[group] = notifications.filter(n => n.group === group).length;
      return acc;
    }, {});

    return {
      total,
      unread,
      byPriority,
      byGroup
    };
  }, [notifications]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
    setPage(0);
  };

  const handleDateRangeChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      dateRange: {
        ...prev.dateRange,
        [field]: value
      }
    }));
    setPage(0);
  };

  const handleClearFilters = () => {
    setFilters({
      group: '',
      priority: '',
      dateRange: {
        start: '',
        end: ''
      }
    });
    setPage(0);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Notification History
      </Typography>

      {/* Analytics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Notifications
              </Typography>
              <Typography variant="h4">
                {analytics.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Unread Notifications
              </Typography>
              <Typography variant="h4">
                {analytics.unread}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                High Priority
              </Typography>
              <Typography variant="h4" color="error">
                {analytics.byPriority[NotificationPriority.HIGH]}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Trade Notifications
              </Typography>
              <Typography variant="h4" color="primary">
                {analytics.byGroup[NotificationGroup.TRADE]}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>Group</InputLabel>
              <Select
                value={filters.group}
                onChange={(e) => handleFilterChange('group', e.target.value)}
                label="Group"
              >
                <MenuItem value="">All Groups</MenuItem>
                {Object.values(NotificationGroup).map((group) => (
                  <MenuItem key={group} value={group}>
                    {group.charAt(0).toUpperCase() + group.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={filters.priority}
                onChange={(e) => handleFilterChange('priority', e.target.value)}
                label="Priority"
              >
                <MenuItem value="">All Priorities</MenuItem>
                {Object.values(NotificationPriority).map((priority) => (
                  <MenuItem key={priority} value={priority}>
                    {priority.charAt(0).toUpperCase() + priority.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                label="Start Date"
                type="date"
                value={filters.dateRange.start}
                onChange={(e) => handleDateRangeChange('start', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
              <TextField
                label="End Date"
                type="date"
                value={filters.dateRange.end}
                onChange={(e) => handleDateRangeChange('end', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Notifications Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Timestamp</TableCell>
              <TableCell>Group</TableCell>
              <TableCell>Message</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredNotifications
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((notification) => (
                <TableRow key={notification.id}>
                  <TableCell>
                    {format(new Date(notification.timestamp), 'PPpp')}
                  </TableCell>
                  <TableCell>
                    <Chip
                      icon={groupIcons[notification.group]}
                      label={notification.group}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{notification.message}</TableCell>
                  <TableCell>
                    <Chip
                      label={notification.priority}
                      color={priorityColors[notification.priority]}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {notification.read ? (
                      <CheckCircleIcon color="success" />
                    ) : (
                      <ErrorIcon color="error" />
                    )}
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        onClick={() => removeNotification(notification.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={filteredNotifications.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>
    </Box>
  );
};

export default NotificationHistory; 