import React, { useEffect, useRef, useState } from 'react';
import { Box, CircularProgress, Typography, useTheme, Alert, Button } from '@mui/material';

const TradingViewWidget = ({ 
  symbol = 'NASDAQ:AAPL', 
  interval = 'D', 
  containerId = 'tradingview_widget',
  height = '100%',
  width = '100%'
}) => {
  const theme = useTheme();
  const containerRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Create a unique ID for this instance
  const uniqueId = useRef(`tv_container_${Math.random().toString(36).substring(2, 9)}`);

  // Initialize widget when component mounts
  useEffect(() => {
    console.log(`Initializing TradingView widget for ${symbol}, interval ${interval}`);
    setIsLoading(true);
    setError(null);

    // Use TradingView's official widget API via embedded script
    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
    script.type = 'text/javascript';
    script.async = true;
    script.innerHTML = JSON.stringify({
      "autosize": true,
      "symbol": symbol,
      "interval": interval,
      "timezone": "Etc/UTC",
      "theme": theme.palette.mode === 'dark' ? "dark" : "light",
      "style": "1",
      "locale": "en",
      "enable_publishing": false,
      "backgroundColor": theme.palette.background.paper,
      "gridColor": theme.palette.divider,
      "allow_symbol_change": true,
      "save_image": false,
      "calendar": false,
      "hide_top_toolbar": false,
      "hide_legend": false,
      "studies": [
        "RSI@tv-basicstudies",
        "MACD@tv-basicstudies"
      ],
      "support_host": "https://www.tradingview.com"
    });
    
    // Get the container
    const container = document.getElementById(uniqueId.current);
    if (container) {
      // Clear existing content
      container.innerHTML = '';
      
      // Create wrapper for TradingView widget
      const widget = document.createElement('div');
      widget.className = 'tradingview-widget-container';
      
      // Create inner div for actual widget
      const widgetDiv = document.createElement('div');
      widgetDiv.className = 'tradingview-widget-container__widget';
      widget.appendChild(widgetDiv);
      
      // Copyright div required by TradingView
      const copyrightDiv = document.createElement('div');
      copyrightDiv.className = 'tradingview-widget-copyright';
      copyrightDiv.innerHTML = '<a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank"><span class="blue-text">Track all markets on TradingView</span></a>';
      widget.appendChild(copyrightDiv);
      
      // Add widget to container
      container.appendChild(widget);
      
      // Add script to container
      widget.appendChild(script);
      
      // Set loading state to false after a delay to allow widget to initialize
      setTimeout(() => {
        setIsLoading(false);
      }, 1000);
      
      // Save reference to clean up
      containerRef.current = { container, widget };
    } else {
      console.error('Container element not found');
      setError('Chart container not found');
      setIsLoading(false);
    }

    // Cleanup function
    return () => {
      if (containerRef.current && containerRef.current.container) {
        try {
          console.log('Cleaning up TradingView container');
          containerRef.current.container.innerHTML = '';
          containerRef.current = null;
        } catch (err) {
          console.error('Error during cleanup:', err);
        }
      }
    };
  }, [symbol, interval, theme.palette.mode]);

  // Handle opening tradingview.com in a new tab
  const openTradingViewWebsite = () => {
    window.open(`https://www.tradingview.com/chart/?symbol=${symbol}`, '_blank');
  };

  return (
    <Box sx={{ position: 'relative', width, height }}>
      <Box
        id={uniqueId.current}
        sx={{ 
          width: '100%', 
          height: '100%',
          '& .tradingview-widget-copyright': {
            fontSize: '12px',
            padding: '4px 8px',
            textAlign: 'center',
            color: theme.palette.text.secondary
          }
        }}
      />
      
      {error && (
        <Box 
          sx={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            width: '100%', 
            height: '100%', 
            display: 'flex', 
            flexDirection: 'column',
            justifyContent: 'center', 
            alignItems: 'center',
            backgroundColor: theme.palette.background.paper,
            zIndex: 5
          }}
        >
          <Alert severity="error" sx={{ mb: 2, maxWidth: '90%' }}>
            {error}
          </Alert>
          <Typography variant="body2" sx={{ mb: 3 }}>
            Unable to load TradingView chart for {symbol}
          </Typography>
          
          <Button
            variant="outlined"
            color="primary"
            onClick={openTradingViewWebsite}
          >
            View on TradingView.com
          </Button>
          
          <Typography variant="caption" sx={{ mt: 3, maxWidth: '80%', textAlign: 'center' }}>
            Try disabling ad blockers or checking your network connection
          </Typography>
        </Box>
      )}
      
      {isLoading && !error && (
        <Box 
          sx={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            width: '100%', 
            height: '100%', 
            display: 'flex', 
            flexDirection: 'column',
            justifyContent: 'center', 
            alignItems: 'center',
            backgroundColor: theme.palette.background.paper,
            zIndex: 5
          }}
        >
          <CircularProgress size={40} />
          <Typography variant="body1" sx={{ mt: 2 }}>
            Loading chart for {symbol}...
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
            This may take a few moments
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default TradingViewWidget; 