import React, { useRef } from 'react';
import { Box, Paper } from '@mui/material';
import ScrollIndicator from './ScrollIndicator';

/**
 * ScrollableContent component
 * Wraps content in a scrollable container with a scroll indicator
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Content to be scrollable
 * @param {string} props.component - Component to use as container ('div', 'paper')
 * @param {number} props.maxHeight - Maximum height of the container
 * @param {string} props.indicatorPosition - Position of scroll indicator
 * @param {number} props.threshold - Scroll threshold to show/hide indicator
 * @param {Object} props.sx - Additional styles for the container
 */
const ScrollableContent = ({
  children,
  component = 'div',
  maxHeight = '70vh',
  indicatorPosition = 'bottom-right',
  threshold = 100,
  sx = {},
}) => {
  const containerRef = useRef(null);
  
  // Choose the container component
  const Container = component === 'paper' ? Paper : Box;
  
  return (
    <Container
      ref={containerRef}
      elevation={component === 'paper' ? 0 : undefined}
      sx={{
        position: 'relative',
        maxHeight,
        overflowY: 'auto',
        paddingRight: '8px', // Add padding to ensure content doesn't overlap with scroll indicator
        ...sx
      }}
    >
      {children}
      
      <ScrollIndicator
        containerRef={containerRef}
        position="bottom-right"
        threshold={threshold}
        offsetBottom={20}
      />
    </Container>
  );
};

export default ScrollableContent; 