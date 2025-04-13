import React, { useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Tooltip
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { useNotification, NotificationPriority, NotificationGroup } from '../contexts/NotificationContext';
import { format, subDays, startOfDay, endOfDay } from 'date-fns';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

const NotificationAnalytics = () => {
  const { notifications } = useNotification();

  const analytics = useMemo(() => {
    const now = new Date();
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = subDays(now, i);
      return {
        date: format(date, 'MMM dd'),
        start: startOfDay(date),
        end: endOfDay(date)
      };
    }).reverse();

    // Daily notifications
    const dailyNotifications = last7Days.map(day => ({
      date: day.date,
      count: notifications.filter(n => {
        const notificationDate = new Date(n.timestamp);
        return notificationDate >= day.start && notificationDate <= day.end;
      }).length
    }));

    // Priority distribution
    const priorityDistribution = Object.values(NotificationPriority).map(priority => ({
      name: priority,
      value: notifications.filter(n => n.priority === priority).length
    }));

    // Group distribution
    const groupDistribution = Object.values(NotificationGroup).map(group => ({
      name: group,
      value: notifications.filter(n => n.group === group).length
    }));

    // Read vs Unread
    const readUnread = {
      read: notifications.filter(n => n.read).length,
      unread: notifications.filter(n => !n.read).length
    };

    // Average response time (time between notification and read)
    const responseTimes = notifications
      .filter(n => n.read)
      .map(n => {
        const created = new Date(n.timestamp);
        const read = new Date(n.readAt);
        return (read - created) / 1000 / 60; // in minutes
      });

    const avgResponseTime = responseTimes.length
      ? responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length
      : 0;

    return {
      dailyNotifications,
      priorityDistribution,
      groupDistribution,
      readUnread,
      avgResponseTime
    };
  }, [notifications]);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <Paper sx={{ p: 2 }}>
          <Typography variant="body2">{`${label}: ${payload[0].value} notifications`}</Typography>
        </Paper>
      );
    }
    return null;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Notification Analytics
      </Typography>

      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Notifications
              </Typography>
              <Typography variant="h4">
                {notifications.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Unread Notifications
              </Typography>
              <Typography variant="h4">
                {analytics.readUnread.unread}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={(analytics.readUnread.unread / notifications.length) * 100}
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                High Priority
              </Typography>
              <Typography variant="h4" color="error">
                {analytics.priorityDistribution.find(p => p.name === NotificationPriority.HIGH)?.value || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Response Time
              </Typography>
              <Typography variant="h4">
                {Math.round(analytics.avgResponseTime)}m
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Daily Notifications Chart */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Daily Notifications
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analytics.dailyNotifications}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <ChartTooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* Distribution Charts */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Priority Distribution
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={analytics.priorityDistribution}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {analytics.priorityDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <ChartTooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Group Distribution
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={analytics.groupDistribution}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {analytics.groupDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <ChartTooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* Detailed Statistics */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Detailed Statistics
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Metric</TableCell>
                    <TableCell align="right">Value</TableCell>
                    <TableCell align="right">Percentage</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {analytics.priorityDistribution.map((priority) => (
                    <TableRow key={priority.name}>
                      <TableCell>{priority.name} Priority</TableCell>
                      <TableCell align="right">{priority.value}</TableCell>
                      <TableCell align="right">
                        {((priority.value / notifications.length) * 100).toFixed(1)}%
                      </TableCell>
                    </TableRow>
                  ))}
                  {analytics.groupDistribution.map((group) => (
                    <TableRow key={group.name}>
                      <TableCell>{group.name} Group</TableCell>
                      <TableCell align="right">{group.value}</TableCell>
                      <TableCell align="right">
                        {((group.value / notifications.length) * 100).toFixed(1)}%
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default NotificationAnalytics; 