import React, { useState, useEffect, useRef } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { 
  Box, 
  Drawer, 
  AppBar, 
  Toolbar, 
  List, 
  Typography, 
  Divider, 
  IconButton, 
  ListItem, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText,
  useTheme,
  Avatar,
  Tooltip,
  Button
} from '@mui/material';
import { 
  Dashboard as DashboardIcon,
  TrendingUp as TrendingUpIcon,
  Timeline as TimelineIcon,
  Settings as SettingsIcon,
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  ExitToApp as ExitToAppIcon,
  Notifications as NotificationsIcon,
  BarChart as BarChartIcon,
  Tune as TuneIcon,
  Analytics as AnalyticsIcon,
  ShowChart as ShowChartIcon,
  Insights as InsightsIcon,
  Security as SecurityIcon,
  SmartToy as SmartToyIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { motion } from 'framer-motion';
import { alpha } from '@mui/material/styles';
import VaultAuth from './VaultAuth';
import { AuthenticatedNotificationBell } from './AuthenticatedContent';
import ScrollIndicator from './ScrollIndicator';

const drawerWidth = 240;

const StyledAppBar = styled(AppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})(({ theme, open }) => ({
  background: 'rgba(10, 14, 23, 0.8)',
  backdropFilter: 'blur(8px)',
  borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
  transition: theme.transitions.create(['margin', 'width'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    width: `calc(100% - ${drawerWidth}px)`,
    marginLeft: `${drawerWidth}px`,
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

const StyledDrawer = styled(Drawer)(({ theme }) => ({
  width: drawerWidth,
  flexShrink: 0,
  '& .MuiDrawer-paper': {
    width: drawerWidth,
    boxSizing: 'border-box',
    background: 'rgba(18, 23, 43, 0.95)',
    backdropFilter: 'blur(10px)',
    borderRight: '1px solid rgba(255, 255, 255, 0.05)',
  },
}));

const StyledNavLink = styled(NavLink)(({ theme }) => ({
  textDecoration: 'none',
  color: 'inherit',
  '&.active .MuiListItemButton-root': {
    background: 'rgba(10, 224, 236, 0.15)',
    borderRight: `3px solid ${theme.palette.primary.main}`,
    '& .MuiListItemIcon-root': {
      color: theme.palette.primary.main,
    },
  },
}));

const GlowingBorder = styled(motion.div)(({ theme }) => ({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  height: '2px',
  background: `linear-gradient(90deg, ${theme.palette.primary.dark}, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
  zIndex: 1000,
}));

const Layout = ({ children }) => {
  const theme = useTheme();
  const [open, setOpen] = useState(true);
  const location = useLocation();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const sidebarRef = useRef(null);

  // Check if user is already authenticated (e.g., from localStorage)
  useEffect(() => {
    const authStatus = localStorage.getItem('vault_authenticated');
    if (authStatus === 'true') {
      setIsAuthenticated(true);
    }
  }, []);

  const handleAuthentication = () => {
    setIsAuthenticated(true);
    localStorage.setItem('vault_authenticated', 'true');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('vault_authenticated');
  };

  const menuItems = [
    { name: 'Dashboard', path: '/', icon: <DashboardIcon /> },
    { name: 'Live Market', path: '/live-market', icon: <ShowChartIcon /> },
    { name: 'Signals', path: '/signals', icon: <TrendingUpIcon /> },
    { name: 'Backtest', path: '/backtest', icon: <TimelineIcon /> },
    { name: 'Market Data', path: '/market-data', icon: <BarChartIcon /> },
    { name: 'TradingView Alerts', path: '/tradingview-alerts', icon: <NotificationsIcon /> },
    { name: 'API Configuration', path: '/market-data-config', icon: <TuneIcon /> },
    { name: 'Market Analysis', path: '/market-analysis', icon: <AnalyticsIcon /> },
    { name: 'Institutional Flow', path: '/institutional-flow', icon: <InsightsIcon /> },
    { name: 'Trade Setups', path: '/trade-setups', icon: <ShowChartIcon /> },
    { name: 'Risk Management', path: '/risk-management', icon: <SecurityIcon /> },
    { name: 'Bot Management', path: '/bot-management', icon: <SmartToyIcon /> },
    { name: 'Settings', path: '/settings', icon: <SettingsIcon /> },
  ];

  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  const renderAuthenticatedContent = () => (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <GlowingBorder 
        initial={{ opacity: 0.5 }}
        animate={{ 
          opacity: [0.5, 1, 0.5], 
          boxShadow: [
            '0 0 5px rgba(10, 224, 236, 0.5)',
            '0 0 15px rgba(10, 224, 236, 0.8)',
            '0 0 5px rgba(10, 224, 236, 0.5)'
          ]
        }}
        transition={{ 
          duration: 2, 
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      
      <StyledAppBar position="fixed" open={open}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerOpen}
            edge="start"
            sx={{ mr: 2, ...(open && { display: 'none' }) }}
          >
            <MenuIcon />
          </IconButton>
          <Typography 
            variant="h6" 
            noWrap 
            component="div" 
            sx={{ 
              flexGrow: 1, 
              fontFamily: 'Orbitron', 
              letterSpacing: '1px',
              fontWeight: 'bold',
              color: theme.palette.primary.main 
            }}
          >
            VELMA
          </Typography>
          
          <AuthenticatedNotificationBell />
          
          <Button
            variant="outlined"
            color="primary"
            onClick={handleLogout}
            startIcon={<ExitToAppIcon />}
            sx={{ 
              mr: 2,
              borderColor: alpha(theme.palette.primary.main, 0.5),
              '&:hover': {
                borderColor: theme.palette.primary.main,
                backgroundColor: alpha(theme.palette.primary.main, 0.1)
              },
              fontFamily: 'Share Tech Mono, monospace',
            }}
          >
            Close Vault
          </Button>
          
          <Tooltip title="User Profile">
            <Avatar 
              src="/images/velma.png" 
              alt="Velma Assistant"
              sx={{ 
                bgcolor: theme.palette.primary.dark,
                border: `1px solid ${theme.palette.primary.main}`,
                boxShadow: `0 0 10px ${theme.palette.primary.main}`
              }}
            />
          </Tooltip>
        </Toolbar>
      </StyledAppBar>
      
      <StyledDrawer
        variant="persistent"
        anchor="left"
        open={open}
      >
        <DrawerHeader>
          <Avatar 
            src="/images/velma.png" 
            alt="Velma Assistant"
            sx={{ 
              height: 45, 
              width: 45, 
              marginRight: 'auto',
              marginLeft: 2,
              border: `2px solid ${theme.palette.primary.main}`,
              backgroundColor: alpha(theme.palette.primary.main, 0.2),
              boxShadow: `0 0 10px ${theme.palette.primary.main}`
            }}
          />
          <IconButton onClick={handleDrawerClose}>
            <ChevronLeftIcon sx={{ color: theme.palette.primary.main }} />
          </IconButton>
        </DrawerHeader>
        
        <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.05)' }} />
        
        <List 
          ref={sidebarRef}
          sx={{ 
            pt: 2,
            pb: 10, 
            overflowY: 'auto',
            maxHeight: 'calc(100vh - 64px - 56px)',
            position: 'relative',
          }}
        >
          {menuItems.map((item) => (
            <ListItem key={item.name} disablePadding>
              <StyledNavLink to={item.path} className={location.pathname === item.path ? 'active' : ''}>
                <ListItemButton>
                  <ListItemIcon>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText 
                    primary={item.name} 
                    primaryTypographyProps={{ 
                      fontFamily: 'Orbitron',
                      fontSize: '0.9rem',
                      letterSpacing: '0.5px'
                    }} 
                  />
                </ListItemButton>
              </StyledNavLink>
            </ListItem>
          ))}
          
          <ScrollIndicator 
            containerRef={sidebarRef} 
            position="bottom-right" 
            threshold={50}
            offsetBottom={70}
            iconStyle={{
              width: 30,
              height: 30,
            }}
          />
        </List>
        
        <Box sx={{ 
          position: 'absolute', 
          bottom: 0, 
          width: '100%', 
          p: 2, 
          textAlign: 'center',
          borderTop: '1px solid rgba(255, 255, 255, 0.05)',
          backgroundColor: 'rgba(18, 23, 43, 0.95)',
          zIndex: 1
        }}>
          <Typography variant="caption" color="text.secondary">
            v2.0 • Velma
          </Typography>
        </Box>
      </StyledDrawer>
      
      <Box component="main" sx={{ 
        flexGrow: 1, 
        p: 3, 
        transition: theme.transitions.create('margin', {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.leavingScreen,
        }),
        marginLeft: `-${drawerWidth}px`,
        ...(open && {
          transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.easeOut,
            duration: theme.transitions.duration.enteringScreen,
          }),
          marginLeft: 0,
        }),
      }}>
        <DrawerHeader />
        {children || <Outlet />}
      </Box>
    </Box>
  );

  return (
    <>
      {!isAuthenticated ? (
        <VaultAuth onAuthenticated={handleAuthentication} />
      ) : (
        renderAuthenticatedContent()
      )}
    </>
  );
};

export default Layout; 