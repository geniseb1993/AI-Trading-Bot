import React from 'react';
import { Card, CardContent, CardHeader, Divider, Typography, alpha, useTheme } from '@mui/material';
import { motion } from 'framer-motion';

/**
 * ContentCard component for consistent card styling across the application
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Card content
 * @param {string} props.title - Card title
 * @param {Object} props.headerAction - Optional header action component
 * @param {Object} props.sx - Additional styling to apply to the card
 * @param {Object} props.contentSx - Additional styling for the card content
 * @param {Object} props.headerSx - Additional styling for the header
 * @param {number} props.animationDelay - Delay for animation (defaults to 0)
 * @returns {JSX.Element}
 */
const ContentCard = ({ 
  children, 
  title, 
  headerAction, 
  sx = {}, 
  contentSx = {}, 
  headerSx = {},
  animationDelay = 0 
}) => {
  const theme = useTheme();
  
  return (
    <Card
      component={motion.div}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: animationDelay }}
      sx={{
        height: '100%',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: alpha(theme.palette.background.paper, 0.7),
        backdropFilter: 'blur(10px)',
        border: `1px solid ${alpha(theme.palette.info.main, 0.3)}`,
        boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.35)}, 0 0 8px ${alpha(theme.palette.primary.main, 0.2)}`,
        borderRadius: 2,
        overflow: 'hidden',
        transition: 'all 0.3s ease',
        '&:hover': {
          boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.4)}, 0 0 12px ${alpha(theme.palette.primary.main, 0.25)}`,
          transform: 'translateY(-2px)'
        },
        position: 'relative',
        m: 0,
        p: 0,
        ...sx
      }}
    >
      {title && (
        <>
          <CardHeader
            title={
              <Typography variant="h6" fontFamily="Orbitron">
                {title}
              </Typography>
            }
            action={headerAction}
            sx={{ 
              flexShrink: 0, 
              height: '60px',
              padding: '8px 16px',
              position: 'relative',
              zIndex: 5,
              ...headerSx
            }}
          />
          <Divider />
        </>
      )}
      <CardContent
        sx={{
          flexGrow: 1,
          height: title ? 'calc(100% - 60px)' : '100%',
          overflow: 'auto',
          padding: '16px',
          '&:last-child': {
            paddingBottom: '16px'
          },
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          margin: 0,
          borderRadius: 0,
          ...contentSx
        }}
      >
        {children}
      </CardContent>
    </Card>
  );
};

export default ContentCard; 