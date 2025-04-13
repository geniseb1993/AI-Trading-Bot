import React from 'react';
import { Grid, Box, useTheme } from '@mui/material';

/**
 * ContentGrid component for consistent grid layouts
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Grid items
 * @param {Object} props.sx - Additional styling
 * @param {number} props.spacing - Grid spacing (defaults to 3)
 * @returns {JSX.Element}
 */
const ContentGrid = ({ children, sx = {}, spacing = 3 }) => {
  const theme = useTheme();

  return (
    <Box 
      sx={{ 
        width: '100%', 
        display: 'flex',
        flexDirection: 'column',
        flexGrow: 1,
        position: 'relative',
        height: '100%',
        m: 0,
        p: 0,
      }}
    >
      <Grid 
        container 
        spacing={spacing} 
        sx={{ 
          display: 'flex',
          width: '100%',
          flexGrow: 1,
          position: 'relative', 
          alignItems: 'stretch',
          height: '100%',
          m: 0,
          p: 0,
          '& .MuiGrid-item': {
            pt: spacing,
            display: 'flex',
          },
          ...sx
        }}
      >
        {children}
      </Grid>
    </Box>
  );
};

export default ContentGrid; 