import React, { useEffect, useState, useRef } from 'react';
import { Box, Typography, CircularProgress, useTheme } from '@mui/material';
import { ResponsiveLine } from '@nivo/line';
import { alpha } from '@mui/material/styles';
import axios from 'axios';

// Add a global error handler for ResizeObserver errors
if (typeof window !== 'undefined') {
  window.addEventListener('error', (event) => {
    if (
      event.message === 'ResizeObserver loop limit exceeded' ||
      event.message.includes('ResizeObserver loop completed with undelivered notifications')
    ) {
      event.stopImmediatePropagation();
    }
  });
}

const TradingChart = ({ selectedSymbol, timeframe, apiConnected = false }) => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState([]);
  const [error, setError] = useState(null);
  // Use ref to prevent unnecessary re-renders that might cause the chart to revert
  const dataFetchedRef = useRef(false);
  const unmountedRef = useRef(false);

  useEffect(() => {
    // Set up the unmounted flag for cleanup
    unmountedRef.current = false;
    
    // Only fetch data if we haven't already or if the dependencies changed
    if (!dataFetchedRef.current || 
        (dataFetchedRef.current && 
         (dataFetchedRef.current.symbol !== selectedSymbol || 
          dataFetchedRef.current.timeframe !== timeframe || 
          dataFetchedRef.current.apiConnected !== apiConnected))) {
      
      setLoading(true);
      setError(null);
      
      const fetchData = async () => {
        try {
          if (apiConnected) {
            // If API is connected, try to fetch real data
            try {
              const response = await axios.post('/api/fetch-data', {
                symbols: [selectedSymbol],
                days: parseInt(timeframe) || 7
              });
              
              if (response.data && response.data.success) {
                const apiData = response.data.data;
                // Process the API data for the chart
                const processedData = processApiData(apiData, selectedSymbol);
                
                // Check if component is still mounted before updating state
                if (!unmountedRef.current) {
                  setChartData(processedData);
                  // Mark as fetched to prevent re-rendering issues
                  dataFetchedRef.current = {
                    symbol: selectedSymbol,
                    timeframe: timeframe,
                    apiConnected: apiConnected
                  };
                  setLoading(false);
                }
                return;
              } else {
                // API returned but with an error
                console.log('API returned unsuccessful response, fallback to demo data');
                throw new Error('API unsuccessful');
              }
            } catch (apiError) {
              console.log('Error fetching from API, falling back to demo data:', apiError);
              // Continue to generate demo data if API fetch fails
            }
          }
          
          // If API is not connected or API fetch failed, generate demo data
          const timerId = setTimeout(() => {
            if (unmountedRef.current) return;
            
            const demoData = generateDemoData(selectedSymbol, parseInt(timeframe) || 7);
            setChartData(demoData);
            // Mark as fetched to prevent re-rendering issues
            dataFetchedRef.current = {
              symbol: selectedSymbol,
              timeframe: timeframe,
              apiConnected: apiConnected
            };
            setLoading(false);
          }, 800);
          
          return () => clearTimeout(timerId);
        } catch (error) {
          console.error('Error fetching chart data:', error);
          if (!unmountedRef.current) {
            setError('Failed to fetch chart data');
            setLoading(false);
          }
        }
      };

      fetchData();
    }
    
    // Cleanup function to handle unmounting
    return () => {
      unmountedRef.current = true;
    };
  }, [selectedSymbol, timeframe, apiConnected, theme]);

  // Process API data for the chart
  const processApiData = (apiData, symbol) => {
    // Filter data for the selected symbol
    const symbolData = apiData.filter(item => item.symbol === symbol);
    
    // Sort by date
    symbolData.sort((a, b) => new Date(a.date) - new Date(b.date));
    
    // Create data point series
    const priceData = { 
      id: symbol, 
      color: theme.palette.primary.main, 
      data: symbolData.map(item => ({
        x: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        y: parseFloat(item.close)
      }))
    };
    
    // Create signal points series (if available)
    const signalPoints = { 
      id: 'signals', 
      color: theme.palette.success.main, 
      data: symbolData
        .filter(item => item.buy_signal === true || item.signal_score > 0) 
        .map(item => ({
          x: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          y: parseFloat(item.close)
        }))
    };
    
    return [priceData, signalPoints];
  };

  const generateDemoData = (symbol, days) => {
    // Ensure days is a positive number
    days = Math.max(7, parseInt(days) || 7);
    
    // Create random price series based on the symbol
    let startPrice;
    let volatility;
    
    switch (symbol) {
      case 'SPY':
        startPrice = 500;
        volatility = 0.01;
        break;
      case 'QQQ':
        startPrice = 430;
        volatility = 0.015;
        break;
      case 'TSLA':
        startPrice = 190;
        volatility = 0.025;
        break;
      case 'AAPL':
        startPrice = 170;
        volatility = 0.015;
        break;
      case 'MSFT':
        startPrice = 410;
        volatility = 0.012;
        break;
      default:
        startPrice = 100;
        volatility = 0.01;
    }

    const priceData = { id: symbol, color: theme.palette.primary.main, data: [] };
    const signalPoints = { id: 'signals', color: theme.palette.success.main, data: [] };
    
    const now = new Date();
    let currentPrice = startPrice;
    
    // Generate multiple price points across different dates
    for (let i = 0; i < days; i++) {
      const date = new Date(now);
      date.setDate(date.getDate() - (days - i - 1));
      const formattedDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      
      // Calculate random price movement (realistic price movement)
      // Using random walk with slight upward bias
      const change = currentPrice * volatility * (Math.random() - 0.45);
      currentPrice += change;
      
      priceData.data.push({
        x: formattedDate,
        y: parseFloat(currentPrice.toFixed(2))
      });
      
      // Add signal points at certain conditions (e.g., significant price increase)
      if (change > 0 && Math.random() > 0.7) {
        signalPoints.data.push({
          x: formattedDate,
          y: parseFloat(currentPrice.toFixed(2))
        });
      }
    }
    
    // Ensure we have at least 2 distinct data points to avoid vertical line
    if (priceData.data.length < 2) {
      priceData.data = [
        { x: "Day 1", y: startPrice },
        { x: "Day 2", y: startPrice * 1.01 }
      ];
    }
    
    // Ensure signalPoints has at least one point to avoid the path prop error
    if (signalPoints.data.length === 0 && priceData.data.length > 0) {
      // Add a signal at a random point if none was added
      const randomIndex = Math.floor(Math.random() * priceData.data.length);
      signalPoints.data.push({
        x: priceData.data[randomIndex].x,
        y: priceData.data[randomIndex].y
      });
    }
    
    return [priceData, signalPoints];
  };

  // Validate chart data to prevent SVG path errors
  const validateChartData = (data) => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      // Return default valid data if no data is provided
      return [
        {
          id: selectedSymbol || 'default',
          color: theme.palette.primary.main,
          data: [
            { x: "Day 1", y: 100 },
            { x: "Day 2", y: 101 }
          ]
        }
      ];
    }
    
    // Check each series
    return data.map(series => {
      // Ensure series has an id and data array
      if (!series.id || !series.data || !Array.isArray(series.data)) {
        return {
          id: series.id || 'default',
          color: series.color || theme.palette.primary.main,
          data: [
            { x: "Day 1", y: 100 },
            { x: "Day 2", y: 101 }
          ]
        };
      }
      
      // If data array is empty, add default points
      if (series.data.length === 0) {
        series.data = [
          { x: "Day 1", y: 100 },
          { x: "Day 2", y: 101 }
        ];
      }
      
      // Ensure each data point has valid x and y values
      series.data = series.data.map(point => ({
        x: point.x || "Unknown",
        y: typeof point.y === 'number' ? point.y : 100
      }));
      
      return series;
    });
  };

  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        width: '100%',
        height: '100%',
        position: 'absolute',
        top: 0,
        left: 0
      }}>
        <CircularProgress size={40} sx={{ color: theme.palette.primary.main }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        width: '100%',
        height: '100%',
        position: 'absolute',
        top: 0,
        left: 0
      }}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  // Validate chart data before rendering
  const validatedChartData = validateChartData(chartData);

  // Render the chart with fixed dimensions to prevent resizing issues
  const renderChart = () => {
    try {
      return (
        <ResponsiveLine
          data={validatedChartData}
          margin={{ top: 20, right: 20, bottom: 60, left: 60 }}
          xScale={{ type: 'point' }}
          yScale={{
            type: 'linear',
            min: 'auto',
            max: 'auto',
            stacked: false,
            reverse: false
          }}
          curve="cardinal"
          axisTop={null}
          axisRight={null}
          axisBottom={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Date',
            legendOffset: 36,
            legendPosition: 'middle',
            color: theme.palette.text.secondary
          }}
          axisLeft={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Price',
            legendOffset: -40,
            legendPosition: 'middle',
            color: theme.palette.text.secondary
          }}
          colors={d => d.color}
          pointSize={10}
          pointColor={{ theme: 'background' }}
          pointBorderWidth={2}
          pointBorderColor={{ from: 'serieColor' }}
          pointLabelYOffset={-12}
          enableArea={true}
          areaOpacity={0.1}
          useMesh={true}
          enableGridX={false}
          enableGridY={true}
          gridYValues={5}
          enableSlices="x"
          enableResponsive={false}
          legends={[
            {
              anchor: 'bottom-right',
              direction: 'row',
              justify: false,
              translateX: 0,
              translateY: 50,
              itemsSpacing: 0,
              itemDirection: 'left-to-right',
              itemWidth: 80,
              itemHeight: 20,
              itemOpacity: 0.75,
              symbolSize: 12,
              symbolShape: 'circle',
              symbolBorderColor: 'rgba(0, 0, 0, .5)',
              effects: [
                {
                  on: 'hover',
                  style: {
                    itemBackground: 'rgba(0, 0, 0, .03)',
                    itemOpacity: 1
                  }
                }
              ]
            }
          ]}
          theme={{
            axis: {
              ticks: {
                text: {
                  fill: theme.palette.text.secondary,
                  fontSize: 12,
                },
              },
              legend: {
                text: {
                  fill: theme.palette.text.primary,
                  fontSize: 12,
                  fontFamily: 'Orbitron',
                },
              },
            },
            grid: {
              line: {
                stroke: alpha(theme.palette.divider, 0.1),
                strokeWidth: 1,
              },
            },
            crosshair: {
              line: {
                stroke: theme.palette.primary.main,
                strokeWidth: 1,
                strokeOpacity: 0.75,
                strokeDasharray: '6 6',
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
            legends: {
              text: {
                fill: theme.palette.text.primary,
                fontFamily: 'Orbitron',
                fontSize: 12,
              },
            },
          }}
        />
      );
    } catch (error) {
      console.error('Error rendering chart:', error);
      return (
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100%' 
        }}>
          <Typography>Chart rendering failed</Typography>
        </Box>
      );
    }
  };

  return (
    <Box sx={{ 
      width: '100%', 
      height: '100%', 
      position: 'relative',
      overflow: 'hidden'
    }}>
      {validatedChartData.length > 0 && validatedChartData[0].data.length > 0 ? (
        <Box sx={{ 
          width: '100%', 
          height: '100%', 
          position: 'absolute', 
          top: 0, 
          left: 0 
        }}>
          {renderChart()}
        </Box>
      ) : (
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100%',
          width: '100%'
        }}>
          <Typography>No chart data available</Typography>
        </Box>
      )}
      
      {/* Glowing overlay effect */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          pointerEvents: 'none',
          background: `radial-gradient(circle at 50% 50%, transparent 70%, ${alpha(theme.palette.background.paper, 0.7)} 100%)`,
          zIndex: 1,
        }}
      />
      
      {!apiConnected && (
        <Box
          sx={{
            position: 'absolute',
            bottom: 60,
            left: 10,
            padding: '3px 6px',
            background: alpha(theme.palette.warning.main, 0.2),
            border: `1px solid ${theme.palette.warning.main}`,
            borderRadius: '4px',
            fontSize: '10px',
            color: theme.palette.warning.main,
            zIndex: 2
          }}
        >
          Demo Data
        </Box>
      )}
    </Box>
  );
};

export default TradingChart;