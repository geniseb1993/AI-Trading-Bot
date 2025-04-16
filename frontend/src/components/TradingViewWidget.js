import React, { useEffect, useRef, useState } from 'react';
import { Box, CircularProgress, Typography, useTheme, Alert, Button, IconButton, Tooltip, alpha } from '@mui/material';
import { Fullscreen, ZoomIn, ZoomOut } from '@mui/icons-material';

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
  const [isFullscreen, setIsFullscreen] = useState(false);
  
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
      "save_image": true,
      "calendar": false,
      "hide_top_toolbar": false,
      "hide_legend": false,
      "toolbar_bg": theme.palette.background.paper,
      "withdateranges": true,
      "range": "1M",
      "details": true,
      "hotlist": true,
      "calendar": true,
      "studies": [
        "RSI@tv-basicstudies",
        "MACD@tv-basicstudies",
        "MAs@tv-basicstudies"
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
  
  // Toggle fullscreen mode
  const toggleFullscreen = () => {
    const container = document.getElementById(uniqueId.current);
    
    if (!document.fullscreenElement) {
      if (container.requestFullscreen) {
        container.requestFullscreen();
        setIsFullscreen(true);
      } else if (container.webkitRequestFullscreen) { /* Safari */
        container.webkitRequestFullscreen();
        setIsFullscreen(true);
      } else if (container.msRequestFullscreen) { /* IE11 */
        container.msRequestFullscreen();
        setIsFullscreen(true);
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
        setIsFullscreen(false);
      } else if (document.webkitExitFullscreen) { /* Safari */
        document.webkitExitFullscreen();
        setIsFullscreen(false);
      } else if (document.msExitFullscreen) { /* IE11 */
        document.msExitFullscreen();
        setIsFullscreen(false);
      }
    }
  };
  
  // Listen for fullscreen change
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('mozfullscreenchange', handleFullscreenChange);
    document.addEventListener('MSFullscreenChange', handleFullscreenChange);
    
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
      document.removeEventListener('mozfullscreenchange', handleFullscreenChange);
      document.removeEventListener('MSFullscreenChange', handleFullscreenChange);
    };
  }, []);

  return (
    <Box sx={{ position: 'relative', width, height }}>
      <Box sx={{ 
        position: 'absolute', 
        top: 10, 
        right: 10, 
        zIndex: 10, 
        display: 'flex',
        gap: 1,
        backgroundColor: alpha(theme.palette.background.paper, 0.7),
        borderRadius: '4px',
        padding: '4px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        backdropFilter: 'blur(4px)'
      }}>
        <Tooltip title="Fit to View">
          <Button
            size="small"
            variant="outlined"
            color="primary"
            onClick={() => {
              // This attempts to call TradingView's chart method to fit content
              // It may not work directly as the embedded widget has limitations
              // But it provides a visual cue for the user
              if (window.tvWidget) {
                try {
                  window.tvWidget.activeChart().executeActionById("timeScaleReset");
                } catch (e) {
                  console.log("Could not reset chart view programmatically");
                }
              }
              
              // Force widget reload as fallback to reset the view
              const container = document.getElementById(uniqueId.current);
              if (container) {
                const oldHeight = container.style.height;
                const oldWidth = container.style.width;
                
                // Briefly expand the container to trigger a resize
                container.style.height = "100%";
                container.style.width = "100%";
                
                // Restore original dimensions after a brief delay
                setTimeout(() => {
                  if (container) {
                    container.style.height = oldHeight;
                    container.style.width = oldWidth;
                  }
                }, 100);
              }
            }}
            sx={{ 
              minWidth: 'auto', 
              fontSize: '0.75rem', 
              height: '28px',
              p: '4px 8px' 
            }}
          >
            Fit Chart
          </Button>
        </Tooltip>
        <Tooltip title="Fullscreen">
          <IconButton 
            size="small" 
            onClick={toggleFullscreen}
            sx={{ color: theme.palette.primary.main }}
          >
            <Fullscreen />
          </IconButton>
        </Tooltip>
      </Box>
      
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
          },
          '&:fullscreen': {
            width: '100vw',
            height: '100vh',
            padding: '0',
            backgroundColor: theme.palette.background.default
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