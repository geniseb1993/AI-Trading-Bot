import React, { useRef, useState, useEffect } from 'react';
import { Box, Container, Typography, useTheme } from '@mui/material';
import ScrollIndicator from './ScrollIndicator';

/**
 * PageLayout component for consistent page layouts
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Page content
 * @param {string} props.title - Page title (optional)
 * @param {boolean} props.scrollIndicator - Whether to show scroll indicator (default: true)
 * @param {Object} props.sx - Additional styling
 * @returns {JSX.Element}
 */
const PageLayout = ({ 
  children, 
  title,
  scrollIndicator = true, 
  sx = {} 
}) => {
  const theme = useTheme();
  const contentRef = useRef(null);
  
  return (
    <Box 
      component="main" 
      sx={{ 
        flexGrow: 1,
        minHeight: '100vh',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden', // Prevent outer scrolling
        ...sx 
      }}
    >
      {title && (
        <Typography 
          variant="h4" 
          component="h1" 
          sx={{ 
            mb: 3, 
            fontFamily: 'Orbitron',
            color: theme.palette.primary.main,
            pl: { xs: 2, sm: 3, md: 4 },
            pt: 2
          }}
        >
          {title}
        </Typography>
      )}
      
      <Container 
        ref={contentRef}
        maxWidth="xl" 
        sx={{ 
          py: 3,
          px: { xs: 2, sm: 3, md: 4 },
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          // Ensure content is scrollable while maintaining full height
          height: title ? 'calc(100vh - 80px)' : 'calc(100vh - 20px)',
          overflowY: 'auto',
          position: 'relative',
          paddingRight: { xs: '24px', sm: '32px', md: '40px' }, // Extra padding to prevent overlap with scroll indicator
        }}
      >
        {children}
        
        {scrollIndicator && (
          <ScrollIndicator 
            containerRef={contentRef} 
            position="bottom-right" 
            threshold={100}
            offsetBottom={30}
          />
        )}
      </Container>
    </Box>
  );
};

export default PageLayout; 