import React, { useState, useEffect, useRef } from 'react';
import { Box, Fade, IconButton } from '@mui/material';
import { KeyboardArrowDown } from '@mui/icons-material';
import { alpha, useTheme } from '@mui/material/styles';

/**
 * ScrollIndicator component
 * Shows a floating animated button when vertical scrolling is possible
 * Automatically disappears when user scrolls down
 * Reappears when scrolled back to top
 * 
 * @param {Object} props
 * @param {React.RefObject} props.containerRef - Reference to the scrollable container
 * @param {string} props.position - Position of the indicator ('sidebar', 'bottom-right', 'bottom-center')
 * @param {number} props.threshold - Scroll threshold in pixels to show/hide indicator (default: 100)
 * @param {number} props.offsetBottom - Offset from bottom in pixels (default: 20) 
 * @param {Object} props.iconStyle - Additional styles for the icon
 */
const ScrollIndicator = ({ 
  containerRef, 
  position = 'bottom-right',
  threshold = 100,
  offsetBottom = 20,
  iconStyle = {}
}) => {
  const theme = useTheme();
  const [visible, setVisible] = useState(false);
  const [initialized, setInitialized] = useState(false);
  const animationRef = useRef(null);

  // Position styles based on the specified position
  const getPositionStyles = () => {
    switch (position) {
      case 'sidebar':
        return {
          position: 'absolute',
          bottom: offsetBottom,
          right: 10,
          zIndex: 1200
        };
      case 'bottom-center':
        return {
          position: 'absolute',
          bottom: offsetBottom,
          right: 10,
          zIndex: 1200
        };
      case 'bottom-right':
      default:
        return {
          position: 'absolute',
          bottom: offsetBottom,
          right: 10,
          zIndex: 1200
        };
    }
  };

  // Pulse animation
  const pulseAnimation = () => {
    let scale = 1;
    let direction = 1;
    const button = document.getElementById('scroll-indicator-button');

    const animate = () => {
      if (!button) return;
      
      // Increment or decrement the scale
      if (scale >= 1.1) direction = -1;
      if (scale <= 0.95) direction = 1;
      
      scale += 0.005 * direction;
      button.style.transform = `scale(${scale})`;
      
      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  };

  // Check if scroll is needed and update visibility
  const checkScroll = () => {
    if (!containerRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    
    // Use a smaller buffer to detect scrollability (10px instead of 0)
    // This helps detect scrollable content more reliably
    const isScrollable = scrollHeight > (clientHeight + 10); 
    const isScrolledDown = scrollTop > threshold;

    // Debug log for troubleshooting
    if (process.env.NODE_ENV === 'development') {
      console.debug('ScrollIndicator check:', {
        scrollHeight, 
        clientHeight,
        isScrollable,
        isScrolledDown,
        scrollTop,
        threshold
      });
    }

    // Only show the indicator if:
    // 1. The container is scrollable
    // 2. The user hasn't scrolled down beyond the threshold or has scrolled back to top
    setVisible(isScrollable && !isScrolledDown);
    
    if (!initialized && isScrollable) {
      setInitialized(true);
    }
  };

  // Scroll down when indicator is clicked
  const handleClick = () => {
    if (!containerRef.current) return;
    
    containerRef.current.scrollBy({
      top: 200,
      behavior: 'smooth'
    });
  };

  // Initialize and set up scroll event listeners
  useEffect(() => {
    const currentContainer = containerRef.current;
    
    if (currentContainer) {
      // Initial check
      checkScroll();
      
      // Set up listeners
      currentContainer.addEventListener('scroll', checkScroll);
      window.addEventListener('resize', checkScroll);
      
      // Additional checks after content might have loaded
      const timeoutId = setTimeout(checkScroll, 500);
      const secondTimeoutId = setTimeout(checkScroll, 1500);
      
      return () => {
        currentContainer.removeEventListener('scroll', checkScroll);
        window.removeEventListener('resize', checkScroll);
        clearTimeout(timeoutId);
        clearTimeout(secondTimeoutId);
      };
    }
  }, [containerRef.current]);

  // Periodically check for scrollability - content may load dynamically
  useEffect(() => {
    const interval = setInterval(checkScroll, 2000);
    return () => clearInterval(interval);
  }, []);

  // Start pulse animation when indicator is visible
  useEffect(() => {
    if (visible) {
      const cleanup = pulseAnimation();
      return cleanup;
    } else if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
  }, [visible]);

  // Only render when initialized and visible
  if (!initialized) return null;

  return (
    <Fade in={visible} timeout={500}>
      <Box sx={getPositionStyles()}>
        <IconButton
          id="scroll-indicator-button"
          onClick={handleClick}
          size="small"
          sx={{
            backgroundColor: alpha(theme.palette.primary.main, 0.2),
            border: `1px solid ${alpha(theme.palette.primary.main, 0.5)}`,
            color: theme.palette.primary.main,
            '&:hover': {
              backgroundColor: alpha(theme.palette.primary.main, 0.3),
            },
            boxShadow: `0 0 10px ${alpha(theme.palette.primary.main, 0.4)}`,
            ...iconStyle,
          }}
        >
          <KeyboardArrowDown />
        </IconButton>
      </Box>
    </Fade>
  );
};

export default ScrollIndicator; 