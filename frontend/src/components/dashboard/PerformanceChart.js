import React, { useMemo } from 'react';
import { Box, Typography, useTheme } from '@mui/material';
import { ResponsiveLine } from '@nivo/line';

/**
 * PerformanceChart component displays portfolio performance over time
 * 
 * @param {Object} props
 * @param {Object} props.performanceData - Performance data object with history array
 * @returns {JSX.Element}
 */
const PerformanceChart = ({ performanceData }) => {
  const theme = useTheme();
  
  // Process data to handle both formats (original and CSV)
  const processedData = useMemo(() => {
    if (!performanceData) return null;

    // Check if we have portfolio_performance data directly
    if (Array.isArray(performanceData)) {
      // Direct array of portfolio_performance - likely from CSV
      return {
        history: performanceData.map(item => ({
          date: item.date,
          value: parseFloat(item.portfolio_value)
        }))
      };
    }
    
    // Check if we have portfolio_performance nested
    if (performanceData.portfolio_performance && Array.isArray(performanceData.portfolio_performance)) {
      return {
        history: performanceData.portfolio_performance.map(item => ({
          date: item.date,
          value: parseFloat(item.portfolio_value)
        }))
      };
    }
    
    // Original format
    return performanceData;
  }, [performanceData]);
  
  if (!processedData || !processedData.history || processedData.history.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
        <Typography>No performance data available</Typography>
      </Box>
    );
  }

  // Format data for Nivo line chart
  const chartData = [
    {
      id: 'portfolio',
      color: theme.palette.primary.main,
      data: processedData.history.map(item => ({
        x: item.date,
        y: item.value
      }))
    }
  ];

  // Calculate performance metrics
  const startValue = processedData.history[0]?.value || 0;
  const endValue = processedData.history[processedData.history.length - 1]?.value || 0;
  const totalReturn = endValue - startValue;
  const totalReturnPercent = startValue !== 0 ? (totalReturn / startValue) * 100 : 0;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Box>
          <Typography variant="body2" color="text.secondary">
            Total Return
          </Typography>
          <Typography 
            variant="h6" 
            color={totalReturn >= 0 ? 'success.main' : 'error.main'}
            fontWeight="bold"
          >
            {totalReturn >= 0 ? '+' : ''}{totalReturn.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ({totalReturnPercent.toFixed(2)}%)
          </Typography>
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary" align="right">
            Starting Value
          </Typography>
          <Typography variant="h6" fontWeight="bold">
            ${startValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </Typography>
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary" align="right">
            Current Value
          </Typography>
          <Typography variant="h6" fontWeight="bold">
            ${endValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </Typography>
        </Box>
      </Box>
      
      <Box sx={{ height: 300, width: '100%' }}>
        <ResponsiveLine
          data={chartData}
          margin={{ top: 20, right: 20, bottom: 50, left: 60 }}
          xScale={{
            type: 'time',
            format: '%Y-%m-%d',
            useUTC: false,
            precision: 'day',
          }}
          xFormat="time:%Y-%m-%d"
          yScale={{
            type: 'linear',
            min: 'auto',
            max: 'auto',
            stacked: false,
            reverse: false
          }}
          curve="monotoneX"
          axisBottom={{
            format: '%b %d',
            tickValues: 'every 7 days',
            legend: 'Date',
            legendOffset: 36,
            legendPosition: 'middle'
          }}
          axisLeft={{
            legend: 'Value ($)',
            legendOffset: -40,
            legendPosition: 'middle'
          }}
          enableGridX={false}
          colors={{ datum: 'color' }}
          lineWidth={3}
          pointSize={0}
          pointColor={{ theme: 'background' }}
          pointBorderWidth={2}
          pointBorderColor={{ from: 'serieColor' }}
          pointLabelYOffset={-12}
          useMesh={true}
          enableSlices="x"
          enableArea={true}
          areaOpacity={0.1}
          crosshairType="cross"
          theme={{
            axis: {
              ticks: {
                text: {
                  fill: theme.palette.text.secondary,
                }
              },
              legend: {
                text: {
                  fill: theme.palette.text.primary,
                }
              }
            },
            grid: {
              line: {
                stroke: theme.palette.divider,
                strokeWidth: 1,
              },
            },
            crosshair: {
              line: {
                stroke: theme.palette.primary.main,
                strokeWidth: 1,
                strokeOpacity: 0.5,
              },
            },
            tooltip: {
              container: {
                background: theme.palette.background.paper,
                color: theme.palette.text.primary,
                fontSize: 12,
                borderRadius: 4,
                boxShadow: '0 4px 10px rgba(0, 0, 0, 0.5)',
              },
            },
          }}
          tooltip={({ point }) => {
            return (
              <Box sx={{ p: 1 }}>
                <Typography variant="body2" fontWeight="bold">
                  {new Date(point.data.x).toLocaleDateString()}
                </Typography>
                <Typography variant="body2">
                  Value: ${point.data.y.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </Typography>
              </Box>
            );
          }}
        />
      </Box>
    </Box>
  );
};

export default PerformanceChart; 