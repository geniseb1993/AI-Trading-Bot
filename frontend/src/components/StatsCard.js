import React from 'react';
import { Box, Card, Typography, alpha, useTheme } from '@mui/material';
import { motion } from 'framer-motion';

const StatsCard = ({ title, value, icon, color }) => {
  const theme = useTheme();

  return (
    <Card
      component={motion.div}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      sx={{
        height: '100%',
        minHeight: 120,
        maxHeight: 140,
        display: 'flex',
        position: 'relative',
        overflow: 'hidden',
        backgroundColor: alpha(theme.palette.background.paper, 0.7),
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.05)',
        boxShadow: `0 4px 20px ${alpha(color, 0.15)}`,
        transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out',
        '&:hover': {
          transform: 'translateY(-5px)',
          boxShadow: `0 6px 25px ${alpha(color, 0.25)}`,
        }
      }}
    >
      <Box 
        sx={{ 
          position: 'absolute',
          top: 0,
          left: 0,
          width: '5px',
          height: '100%',
          backgroundColor: color,
          boxShadow: `0 0 10px ${color}`,
        }} 
      />
      
      <Box 
        sx={{ 
          display: 'flex',
          flexDirection: 'column',
          width: '100%',
          flex: 1,
          p: 3,
          pl: 4, // To accommodate the colored bar
          justifyContent: 'space-between'
        }}
      >
        <Typography 
          variant="h6" 
          fontFamily="Orbitron"
          fontSize="0.9rem"
          letterSpacing="0.5px"
          color="text.secondary"
          mb={2}
          sx={{ flexShrink: 0 }}
        >
          {title}
        </Typography>
        
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          flexShrink: 0
        }}>
          <Typography 
            variant="h4" 
            fontFamily="Orbitron"
            fontWeight="bold"
            sx={{ 
              color: theme.palette.text.primary,
              textShadow: `0 0 10px ${alpha(color, 0.5)}`,
              fontSize: { xs: '1.5rem', sm: '1.8rem', md: '2rem' }
            }}
          >
            {value}
          </Typography>
          
          <Box sx={{ 
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 50,
            height: 50,
            borderRadius: '50%',
            backgroundColor: alpha(color, 0.15),
            color: color,
            transition: 'transform 0.3s ease',
            flexShrink: 0,
            '&:hover': {
              transform: 'scale(1.1)',
              backgroundColor: alpha(color, 0.25),
            }
          }}>
            {icon}
          </Box>
        </Box>
      </Box>
    </Card>
  );
};

export default StatsCard; 