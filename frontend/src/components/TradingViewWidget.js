import React, { useEffect, useRef, useCallback } from 'react';
import './TradingViewWidget.css';

const TradingViewWidget = (props) => {
  const containerRef = useRef(null);
  const scriptRef = useRef(null);
  const widgetRef = useRef(null);
  const isMountedRef = useRef(true);
  
  // Generate a unique ID for this widget instance
  const widgetId = useRef(`tradingview_${Math.random().toString(36).substring(2, 15)}`);
  
  // Format the symbol for TradingView
  const formatSymbol = (symbol) => {
    if (!symbol) return 'NASDAQ:AAPL';
    // Handle crypto and forex
    if (symbol.includes('/')) {
      return symbol.replace('/', '');
    }
    // Add NASDAQ prefix if not present
    if (!symbol.includes(':')) {
      return `NASDAQ:${symbol}`;
    }
    return symbol;
  };

  // Clean up function
  const cleanupWidget = useCallback(() => {
    console.log('Cleaning up TradingView widget...');
    
    // First safely remove the widget if it exists
    if (window.tvWidget) {
      try {
        // Check if the widget has a remove method and it's a function
        if (window.tvWidget && typeof window.tvWidget.remove === 'function') {
          window.tvWidget.remove();
        }
        window.tvWidget = null;
      } catch (e) {
        console.warn('Error removing TradingView widget:', e);
      }
    }
    
    // Clean widgetRef
    widgetRef.current = null;
    
    // Handle script element cleanup - only if the script exists and is in the document
    if (scriptRef.current && document.head.contains(scriptRef.current)) {
      try {
        document.head.removeChild(scriptRef.current);
      } catch (e) {
        console.warn('Error removing script element:', e);
      }
      scriptRef.current = null;
    }
    
    // Safe cleanup of container contents
    if (containerRef.current) {
      // Use a safer approach to clear the container
      while (containerRef.current.firstChild) {
        containerRef.current.removeChild(containerRef.current.firstChild);
      }
    }
  }, []);

  // Create widget function with error handling
  const createWidget = useCallback(() => {
    // Safety check - ensure component is still mounted
    if (!isMountedRef.current) return;
    
    // Safety check - ensure container exists
    if (!containerRef.current) return;
    
    // Clear container first - safely
    if (containerRef.current) {
      while (containerRef.current.firstChild) {
        containerRef.current.removeChild(containerRef.current.firstChild);
      }
    }
    
    // Create new container div inside our ref container
    const widgetContainer = document.createElement('div');
    widgetContainer.id = widgetId.current;
    widgetContainer.style.width = '100%';
    widgetContainer.style.height = '100%';
    containerRef.current.appendChild(widgetContainer);
    
    // Load TradingView script
    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/tv.js';
    script.async = true;
    script.onload = () => {
      // Safety check - ensure component is still mounted
      if (!isMountedRef.current) {
        script.remove();
        return;
      }
      
      if (typeof window.TradingView === 'undefined') {
        console.error('TradingView library not loaded properly');
        return;
      }
      
      const symbol = formatSymbol(props.symbol || 'NASDAQ:AAPL');
      const interval = props.interval || 'D';
      
      console.log(`Initializing TradingView widget for ${symbol}, interval ${interval}`);
      
      // Wait for DOM to settle before creating widget
      setTimeout(() => {
        if (!isMountedRef.current || !containerRef.current) return;
        
        try {
          // Check if widgetContainer still exists in the DOM
          if (!document.getElementById(widgetId.current)) {
            console.warn('Widget container no longer exists in DOM');
            return;
          }
          
          // Enhanced widget configuration with width/height props
          const widgetOptions = {
            symbol: symbol,
            interval: interval,
            container_id: widgetId.current,
            locale: 'en',
            autosize: true,
            fullscreen: false,
            theme: 'Dark',
            allow_symbol_change: true,
            width: '100%',
            height: '100%',
            save_image: false,
            hide_side_toolbar: false,
            enable_publishing: false,
            show_popup_button: true,
            withdateranges: true
          };
          
          // Create the widget
          const tvWidget = new window.TradingView.widget(widgetOptions);
          
          // Store reference to widget
          if (isMountedRef.current) {
            widgetRef.current = tvWidget;
            window.tvWidget = tvWidget;
            
            // Additional tweaks to ensure full width after widget creation
            const container = document.getElementById(widgetId.current);
            if (container) {
              setTimeout(() => {
                const frameEl = container.querySelector('iframe');
                if (frameEl) {
                  frameEl.style.width = '100%';
                  frameEl.style.height = '100%';
                }
              }, 500);
            }
          } else {
            // If component unmounted during initialization
            if (tvWidget && typeof tvWidget.remove === 'function') {
              tvWidget.remove();
            }
          }
        } catch (e) {
          console.error('Error creating TradingView widget:', e);
        }
      }, 300);
    };
    
    script.onerror = () => {
      console.error('Failed to load TradingView script');
      if (scriptRef.current === script) {
        scriptRef.current = null;
      }
    };
    
    // Clean up any existing script before adding a new one
    if (scriptRef.current && document.head.contains(scriptRef.current)) {
      document.head.removeChild(scriptRef.current);
    }
    
    // Add script to document
    document.head.appendChild(script);
    scriptRef.current = script;
  }, [props.symbol, props.interval, cleanupWidget]);

  useEffect(() => {
    // Track mounted state
    isMountedRef.current = true;
    
    // Initialize widget on mount
    if (containerRef.current) {
      // Use setTimeout to ensure DOM is ready
      setTimeout(createWidget, 100);
    }
    
    // Cleanup on unmount
    return () => {
      isMountedRef.current = false;
      cleanupWidget();
    };
  }, [createWidget, cleanupWidget]);

  // Also re-initialize when symbol or interval changes
  useEffect(() => {
    if (containerRef.current) {
      // Remove old widget first
      cleanupWidget();
      
      // Create new widget with updated props
      setTimeout(createWidget, 300);
    }
  }, [props.symbol, props.interval, cleanupWidget, createWidget]);

  return (
    <div 
      ref={containerRef}
      className="tradingview-widget-container"
      style={{ width: '100%', height: '100%', minHeight: '600px' }}
    />
  );
};

export default TradingViewWidget; 