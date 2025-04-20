import React, { useEffect, useRef, useState } from 'react';
import { Box, CircularProgress, Typography, useTheme, Alert, Button, IconButton, Tooltip, alpha } from '@mui/material';
import { Fullscreen, ZoomIn, ZoomOut, Refresh, OpenInNew } from '@mui/icons-material';

const TradingViewWidget = ({ 
  symbol = 'NASDAQ:AAPL', 
  interval = 'D', 
  containerId = 'tradingview_widget',
  height = '100%',
  width = '100%'
}) => {
  const theme = useTheme();
  const containerRef = useRef(null);
  const scriptRef = useRef(null);
  const widgetRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  
  // Create a unique ID for this instance
  const uniqueId = useRef(`tv_container_${Math.random().toString(36).substring(2, 9)}`);

  // Cleanup function to safely remove the widget and script
  const cleanupWidget = () => {
    try {
      // Clean up widget instance if it exists
      if (window.tvWidget) {
        try {
          window.tvWidget.remove();
          window.tvWidget = null;
        } catch (err) {
          console.warn('Error removing TradingView widget:', err);
        }
      }
      
      // Remove script element if it exists
      if (scriptRef.current) {
        try {
          document.body.removeChild(scriptRef.current);
          scriptRef.current = null;
        } catch (err) {
          console.warn('Error removing script element:', err);
        }
      }
      
      // Clear container contents if it exists
      if (containerRef.current) {
        try {
          containerRef.current.innerHTML = '';
        } catch (err) {
          console.warn('Error clearing container:', err);
        }
      }
    } catch (err) {
      console.warn('Error during cleanup:', err);
    }
  };

  // Initialize widget when component mounts
  useEffect(() => {
    // Cleanup any existing widget first
    cleanupWidget();
    
    const loadWidget = () => {
    console.log(`Initializing TradingView widget for ${symbol}, interval ${interval}`);
    setIsLoading(true);
    setError(null);

      try {
        // Get the container - use the ref directly instead of getElementById
        if (!containerRef.current) {
          console.error('Container ref is null');
          setError('Chart container not available');
          setIsLoading(false);
          return;
        }

        // Clear existing content
        containerRef.current.innerHTML = '';
        
        // Create a simple container for the widget
        const widgetContainer = document.createElement('div');
        widgetContainer.className = 'tradingview-widget-container';
        widgetContainer.style.width = '100%';
        widgetContainer.style.height = '100%';
        
        // Create inner div for actual widget
        const widgetDiv = document.createElement('div');
        widgetDiv.id = `${uniqueId.current}_inner`;
        widgetDiv.className = 'tradingview-widget-container__widget';
        widgetDiv.style.width = '100%';
        widgetDiv.style.height = '100%';
        widgetContainer.appendChild(widgetDiv);
        
        // Add container to DOM
        containerRef.current.appendChild(widgetContainer);
        
        // Save reference to widget div
        widgetRef.current = widgetDiv;
        
        // Double check to make sure parent node is available
        if (!widgetDiv.parentNode) {
          console.error('Widget div has no parent node');
          setError('Widget container error');
          setIsLoading(false);
          return;
        }
        
        // Create script element - use a different approach with Widget Constructor API
    const script = document.createElement('script');
        script.src = 'https://s3.tradingview.com/tv.js';
    script.type = 'text/javascript';
    script.async = true;
        
        // Save script reference for cleanup
        scriptRef.current = script;
        
        // When script loads, create the widget
        script.onload = () => {
          if (typeof window.TradingView === 'undefined') {
            setError('TradingView library failed to load');
            setIsLoading(false);
            return;
          }
          
          // Make sure the widget div still exists in the DOM
          if (!document.getElementById(widgetDiv.id)) {
            console.error('Widget div no longer in DOM');
            setError('Widget container removed from DOM');
            setIsLoading(false);
            return;
          }
          
          try {
            // Create new widget with simpler, more reliable method
            const widgetOptions = {
              "container_id": widgetDiv.id,
      "autosize": true,
      "symbol": symbol,
      "interval": interval,
      "timezone": "Etc/UTC",
      "theme": theme.palette.mode === 'dark' ? "dark" : "light",
      "style": "1",
      "locale": "en",
              "toolbar_bg": theme.palette.background.paper,
      "enable_publishing": false,
      "hide_top_toolbar": false,
      "hide_legend": false,
              "save_image": true,
      "studies": [
        "RSI@tv-basicstudies",
                "MACD@tv-basicstudies",
                "StochasticRSI@tv-basicstudies"
              ],
              "show_popup_button": true,
              "popup_width": "1000",
              "popup_height": "650",
              "withdateranges": true,
              "details": true
            };
            
            // Support for newer TradingView library API which might have different methods
            try {
              // Instead of declaring onChartReady in the options, we'll use events
              window.tvWidget = new window.TradingView.widget(widgetOptions);
              
              // Set up a proper event listener for chart ready
              let readyTimeout;
              
              // Try to detect if the library has the addEventListener method
              if (window.tvWidget && typeof window.tvWidget.addEventListener === 'function') {
                window.tvWidget.addEventListener('onChartReady', () => {
                  console.log('Chart ready via addEventListener');
                  clearTimeout(readyTimeout);
                  setIsLoading(false);
                });
              } else {
                // Use the onChartReady method if available (traditional approach)
                console.log('Using traditional onChartReady approach');
                
                // Wait for the chart to be ready
                const checkChartReady = () => {
                  if (window.tvWidget && typeof window.tvWidget.onChartReady === 'function') {
                    window.tvWidget.onChartReady(() => {
                      console.log('Chart ready via onChartReady');
                      setIsLoading(false);
                    });
                  } else {
                    // Set a timeout as a fallback
                    console.log('Using fallback for chart ready detection');
                    setTimeout(() => {
                      setIsLoading(false);
                    }, 2500);
                  }
                };
                
                // Check after a small delay to allow widget to initialize
                setTimeout(checkChartReady, 100);
              }
              
              // Fallback timeout in case none of the event handlers work
              readyTimeout = setTimeout(() => {
                console.log('Chart ready via timeout fallback');
                setIsLoading(false);
              }, 3000);
              
              // Check for iframe load as another way to detect readiness
              setTimeout(() => {
                const iframe = document.querySelector(`#${widgetDiv.id} iframe`);
                if (iframe) {
                  iframe.addEventListener('load', () => {
                    console.log('Chart ready via iframe load');
                    clearTimeout(readyTimeout);
                    setIsLoading(false);
                  });
                }
              }, 300);
              
            } catch (err) {
              console.error('Error setting up chart ready event:', err);
              // Fallback to timeout approach
              setTimeout(() => {
                setIsLoading(false);
              }, 2500);
            }
          } catch (err) {
            console.error('Error creating TradingView widget:', err);
            setError('Error creating chart: ' + err.message);
            setIsLoading(false);
          }
        };
        
        // Error handling for script load failure
        script.onerror = (err) => {
          console.error('Error loading TradingView script:', err);
          setError('Failed to load TradingView library');
          setIsLoading(false);
        };
        
        // Add script to document
        document.body.appendChild(script);
      } catch (err) {
        console.error('Error in TradingView widget setup:', err);
        setError(err.message || 'Error setting up chart');
      setIsLoading(false);
    }
    };
    
    // Delay loading to ensure DOM is ready
    const timerId = setTimeout(loadWidget, 1000);  // Increased delay for better DOM readiness

    // Cleanup function
    return () => {
      clearTimeout(timerId);
      cleanupWidget();
    };
  }, [symbol, interval, theme.palette.mode, retryCount]);

  // Handle opening tradingview.com in a new tab
  const openTradingViewWebsite = () => {
    window.open(`https://www.tradingview.com/chart/?symbol=${symbol}`, '_blank');
  };
  
  // Toggle fullscreen mode
  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    
    if (!document.fullscreenElement) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen();
        setIsFullscreen(true);
      } else if (containerRef.current.webkitRequestFullscreen) { /* Safari */
        containerRef.current.webkitRequestFullscreen();
        setIsFullscreen(true);
      } else if (containerRef.current.msRequestFullscreen) { /* IE11 */
        containerRef.current.msRequestFullscreen();
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
  
  // Retry loading the widget
  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
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
    <Box sx={{ position: 'relative', width, height, display: 'flex', flexDirection: 'column' }}>
      {error && (
        <Alert 
          severity="error" 
          sx={{ m: 1 }}
          action={
            <Button color="inherit" size="small" onClick={handleRetry}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      )}
      
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
        <Tooltip title="Reload Chart">
          <IconButton 
            size="small" 
            onClick={handleRetry}
            sx={{ color: theme.palette.primary.main }}
          >
            <Refresh />
          </IconButton>
        </Tooltip>
        <Tooltip title="Open in TradingView">
          <IconButton 
            size="small" 
            onClick={openTradingViewWebsite}
            sx={{ color: theme.palette.primary.main }}
          >
            <OpenInNew />
          </IconButton>
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
        ref={containerRef}
        id={uniqueId.current}
        sx={{ 
          width: '100%', 
          height: '100%',
          position: 'relative',
          flex: 1,
          '& .tradingview-widget-copyright': {
            fontSize: '12px',
            padding: '4px 8px',
            textAlign: 'center',
            color: theme.palette.text.secondary
          }
        }}
      />
      
      {isLoading && (
        <Box 
          sx={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            right: 0, 
            bottom: 0, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            backgroundColor: alpha(theme.palette.background.paper, 0.5)
          }}
        >
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress size={40} />
            <Typography sx={{ mt: 2 }}>Loading Chart...</Typography>
          </Box>
        </Box>
      )}
      
      <Box sx={{ 
        p: 1, 
            display: 'flex', 
            justifyContent: 'center', 
        borderTop: `1px solid ${theme.palette.divider}`,
        backgroundColor: alpha(theme.palette.background.paper, 0.8)
      }}>
        <Typography variant="caption" color="text.secondary">
          <a href="https://www.tradingview.com/" rel="noopener noreferrer" target="_blank" style={{
            color: theme.palette.primary.main,
            textDecoration: 'none'
          }}>
            Powered by TradingView
          </a>
          </Typography>
        </Box>
    </Box>
  );
};

export default TradingViewWidget; 