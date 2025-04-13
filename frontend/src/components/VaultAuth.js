import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  TextField,
  Paper,
  alpha,
  useTheme,
  Modal,
  CircularProgress,
  IconButton,
  Divider,
  Fade,
  Grid,
  Chip,
  Backdrop,
  Tooltip,
  Switch,
  FormControlLabel
} from '@mui/material';
import { motion, AnimatePresence, MotionConfig } from 'framer-motion';
import { Lock, Fingerprint, ErrorOutline, CheckCircleOutline, Close as CloseIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import TimelineIcon from '@mui/icons-material/Timeline';
import SpeedIcon from '@mui/icons-material/Speed';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import BarChartIcon from '@mui/icons-material/BarChart';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, LineChart, Line, CartesianGrid, Legend, AreaChart, Area } from 'recharts';

// Fixed PIN
const CORRECT_PIN = '8080';

const StartupIntelligenceModal = ({ open, onClose }) => {
  const theme = useTheme();
  const [showOnStartup, setShowOnStartup] = useState(true);
  const [chartVisible, setChartVisible] = useState(false);
  
  // Add useEffect to control chart rendering to prevent ResizeObserver errors
  useEffect(() => {
    if (open) {
      // Delay chart rendering to prevent ResizeObserver errors during animation
      const timer = setTimeout(() => {
        setChartVisible(true);
      }, 300);
      
      return () => clearTimeout(timer);
    } else {
      setChartVisible(false);
    }
  }, [open]);
  
  // Mock data for the modal
  const tradeData = {
    today: 3,
    week: 12,
    total: 87,
    winRatio: 68,
    profit: 12.4,
    openPositions: [
      { symbol: 'SPY', direction: 'long', entryPrice: 458.75, currentPrice: 462.30, profit: 0.77 },
      { symbol: 'MSFT', direction: 'long', entryPrice: 385.20, currentPrice: 390.45, profit: 1.36 },
      { symbol: 'AAPL', direction: 'short', entryPrice: 188.25, currentPrice: 185.60, profit: 1.41 }
    ],
    recentTrades: [
      { symbol: 'QQQ', result: 'win', profit: 2.3, date: '2023-06-10', exitReason: 'Take profit hit' },
      { symbol: 'TSLA', result: 'loss', profit: -1.1, date: '2023-06-09', exitReason: 'Stop loss hit' },
      { symbol: 'NVDA', result: 'win', profit: 3.5, date: '2023-06-08', exitReason: 'AI decision' }
    ]
  };
  
  const accountData = {
    balance: 25840.75,
    realized: 3245.60,
    unrealized: 842.30,
    maxDrawdown: 5.2,
    roi: 18.4,
    riskLevel: 'Medium'
  };
  
  const pieData = [
    { name: 'Wins', value: 68 },
    { name: 'Losses', value: 32 }
  ];
  
  const COLORS = ['#00C49F', '#FF8042'];
  
  const monthlyPerformance = [
    { name: 'Jan', profit: 2.1 },
    { name: 'Feb', profit: 1.8 },
    { name: 'Mar', profit: -0.7 },
    { name: 'Apr', profit: 3.2 },
    { name: 'May', profit: 2.5 },
    { name: 'Jun', profit: 1.9 }
  ];
  
  const aiDecisionData = [
    { name: 'Technical', value: 40 },
    { name: 'Fundamental', value: 25 },
    { name: 'Sentiment', value: 20 },
    { name: 'Flow', value: 15 }
  ];
  
  const handleToggleShowOnStartup = () => {
    setShowOnStartup(!showOnStartup);
    // In a real app, you would save this preference to localStorage or user settings
    localStorage.setItem('showStartupModal', (!showOnStartup).toString());
  };
  
  return (
    <Modal
      open={open}
      onClose={onClose}
      closeAfterTransition
      BackdropComponent={Backdrop}
      BackdropProps={{
        timeout: 500,
      }}
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <Fade in={open}>
        <Paper
          sx={{
            width: '90%',
            maxWidth: '1200px',
            maxHeight: '90vh',
            overflow: 'auto',
            p: 3,
            backgroundColor: theme => alpha(theme.palette.background.paper, 0.9),
            backdropFilter: 'blur(10px)',
            border: theme => `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
            borderRadius: 2,
            boxShadow: theme => `0 8px 32px ${alpha(theme.palette.primary.main, 0.2)}`,
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" sx={{ fontFamily: 'Orbitron', color: theme => theme.palette.primary.main }}>
              <AutoGraphIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              AI Trading Intelligence Dashboard
            </Typography>
            <IconButton onClick={onClose} color="primary">
              <CloseIcon />
            </IconButton>
          </Box>
          
          <Divider sx={{ mb: 3 }} />
          
          <Grid container spacing={3}>
            {/* AI Bot Performance Overview */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, borderRadius: 2, height: '100%', boxShadow: 2 }}>
                <Typography variant="h6" sx={{ fontFamily: 'Orbitron', mb: 2, display: 'flex', alignItems: 'center' }}>
                  <ShowChartIcon sx={{ mr: 1 }} /> AI Bot Performance
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">Win Ratio</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography variant="h4" sx={{ fontFamily: 'Orbitron', mr: 1 }}>
                          {tradeData.winRatio}%
                        </Typography>
                        {chartVisible && (
                          <ResponsiveContainer width={80} height={40}>
                            <PieChart>
                              <Pie
                                data={pieData}
                                cx="50%"
                                cy="50%"
                                innerRadius={15}
                                outerRadius={20}
                                paddingAngle={2}
                                dataKey="value"
                              >
                                {pieData.map((entry, index) => (
                                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                              </Pie>
                            </PieChart>
                          </ResponsiveContainer>
                        )}
                      </Box>
                    </Box>
                    
                    <Box>
                      <Typography variant="body2" color="text.secondary">Profit/Loss</Typography>
                      <Typography 
                        variant="h5" 
                        sx={{ 
                          fontFamily: 'Orbitron', 
                          color: tradeData.profit >= 0 ? 'success.main' : 'error.main',
                          display: 'flex',
                          alignItems: 'center'
                        }}
                      >
                        {tradeData.profit >= 0 ? <TrendingUpIcon sx={{ mr: 0.5 }} /> : <TrendingDownIcon sx={{ mr: 0.5 }} />}
                        {tradeData.profit}%
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <Chip 
                        icon={<ShowChartIcon />} 
                        label={`Today: ${tradeData.today} trades`} 
                        color="primary" 
                        variant="outlined" 
                      />
                      <Chip 
                        icon={<ShowChartIcon />} 
                        label={`This Week: ${tradeData.week} trades`} 
                        color="primary" 
                        variant="outlined" 
                      />
                      <Chip 
                        icon={<ShowChartIcon />} 
                        label={`Total: ${tradeData.total} trades`} 
                        color="primary" 
                        variant="outlined" 
                      />
                    </Box>
                  </Grid>
                </Grid>
                
                <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>Monthly Performance</Typography>
                {chartVisible && (
                  <ResponsiveContainer width="100%" height={100}>
                    <AreaChart data={monthlyPerformance}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 10 }} />
                      <RechartsTooltip />
                      <Area type="monotone" dataKey="profit" stroke="#8884d8" fill="#8884d8" />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </Paper>
            </Grid>
            
            {/* Account Metrics */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, borderRadius: 2, height: '100%', boxShadow: 2 }}>
                <Typography variant="h6" sx={{ fontFamily: 'Orbitron', mb: 2, display: 'flex', alignItems: 'center' }}>
                  <AccountBalanceIcon sx={{ mr: 1 }} /> Account Metrics
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Account Balance</Typography>
                    <Typography variant="h5" sx={{ fontFamily: 'Orbitron', display: 'flex', alignItems: 'center' }}>
                      <MonetizationOnIcon sx={{ mr: 0.5, fontSize: '1.2rem' }} />
                      ${accountData.balance.toLocaleString()}
                    </Typography>
                    
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" color="text.secondary">ROI</Typography>
                      <Typography variant="h6" sx={{ fontFamily: 'Orbitron', color: 'success.main' }}>
                        {accountData.roi}%
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">Realized P/L</Typography>
                      <Typography 
                        variant="body1" 
                        sx={{ 
                          fontWeight: 'bold',
                          color: accountData.realized >= 0 ? 'success.main' : 'error.main'
                        }}
                      >
                        ${accountData.realized.toLocaleString()}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">Unrealized P/L</Typography>
                      <Typography 
                        variant="body1" 
                        sx={{ 
                          fontWeight: 'bold',
                          color: accountData.unrealized >= 0 ? 'success.main' : 'error.main'
                        }}
                      >
                        ${accountData.unrealized.toLocaleString()}
                      </Typography>
                    </Box>
                    
                    <Box>
                      <Typography variant="body2" color="text.secondary">Max Drawdown</Typography>
                      <Typography variant="body1" sx={{ fontWeight: 'bold', color: 'error.main' }}>
                        {accountData.maxDrawdown}%
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
                
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>Risk Level</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <SpeedIcon sx={{ color: accountData.riskLevel === 'Low' ? 'success.main' : 
                              accountData.riskLevel === 'Medium' ? 'warning.main' : 'error.main', mr: 1 }} />
                    <Typography 
                      variant="body1" 
                      sx={{ 
                        fontWeight: 'bold',
                        color: accountData.riskLevel === 'Low' ? 'success.main' : 
                              accountData.riskLevel === 'Medium' ? 'warning.main' : 'error.main'
                      }}
                    >
                      {accountData.riskLevel} Risk
                    </Typography>
                  </Box>
                </Box>
                
                <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>AI Decision Factors</Typography>
                {chartVisible && (
                  <ResponsiveContainer width="100%" height={100}>
                    <BarChart data={aiDecisionData}>
                      <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 10 }} />
                      <RechartsTooltip />
                      <Bar dataKey="value" fill="#82ca9d" />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </Paper>
            </Grid>
            
            {/* Open Positions */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, borderRadius: 2, height: '100%', boxShadow: 2 }}>
                <Typography variant="h6" sx={{ fontFamily: 'Orbitron', mb: 2, display: 'flex', alignItems: 'center' }}>
                  <TimelineIcon sx={{ mr: 1 }} /> Current Open Positions
                </Typography>
                
                {tradeData.openPositions.length > 0 ? (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {tradeData.openPositions.map((position, index) => (
                      <Paper 
                        key={index} 
                        sx={{ 
                          p: 1.5, 
                          borderRadius: 1,
                          border: position.direction === 'long' ? '1px solid rgba(0, 200, 83, 0.2)' : '1px solid rgba(255, 72, 66, 0.2)',
                          bgcolor: position.direction === 'long' ? 'rgba(0, 200, 83, 0.05)' : 'rgba(255, 72, 66, 0.05)',
                        }}
                      >
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography variant="h6" sx={{ fontFamily: 'Orbitron', mr: 1 }}>
                              {position.symbol}
                            </Typography>
                            <Chip 
                              size="small"
                              label={position.direction.toUpperCase()}
                              color={position.direction === 'long' ? 'success' : 'error'}
                              icon={position.direction === 'long' ? <TrendingUpIcon /> : <TrendingDownIcon />}
                            />
                          </Box>
                          <Typography 
                            variant="body1" 
                            sx={{ 
                              fontWeight: 'bold',
                              color: position.profit >= 0 ? 'success.main' : 'error.main'
                            }}
                          >
                            {position.profit >= 0 ? '+' : ''}{position.profit}%
                          </Typography>
                        </Box>
                        
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                          <Typography variant="body2" color="text.secondary">
                            Entry: ${position.entryPrice}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Current: ${position.currentPrice}
                          </Typography>
                        </Box>
                      </Paper>
                    ))}
                  </Box>
                ) : (
                  <Typography variant="body1" sx={{ textAlign: 'center', py: 2 }}>
                    No open positions at this time
                  </Typography>
                )}
              </Paper>
            </Grid>
            
            {/* Recent Trades */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, borderRadius: 2, height: '100%', boxShadow: 2 }}>
                <Typography variant="h6" sx={{ fontFamily: 'Orbitron', mb: 2, display: 'flex', alignItems: 'center' }}>
                  <BarChartIcon sx={{ mr: 1 }} /> Recent Trade Insights
                </Typography>
                
                {tradeData.recentTrades.length > 0 ? (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {tradeData.recentTrades.map((trade, index) => (
                      <Paper 
                        key={index} 
                        sx={{ 
                          p: 1.5, 
                          borderRadius: 1, 
                          border: trade.result === 'win' ? '1px solid rgba(0, 200, 83, 0.2)' : '1px solid rgba(255, 72, 66, 0.2)',
                          bgcolor: trade.result === 'win' ? 'rgba(0, 200, 83, 0.05)' : 'rgba(255, 72, 66, 0.05)',
                        }}
                      >
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography variant="h6" sx={{ fontFamily: 'Orbitron', mr: 1 }}>
                              {trade.symbol}
                            </Typography>
                            <Chip 
                              size="small"
                              label={trade.result.toUpperCase()}
                              color={trade.result === 'win' ? 'success' : 'error'}
                            />
                          </Box>
                          <Typography 
                            variant="body1" 
                            sx={{ 
                              fontWeight: 'bold',
                              color: trade.profit >= 0 ? 'success.main' : 'error.main'
                            }}
                          >
                            {trade.profit >= 0 ? '+' : ''}{trade.profit}%
                          </Typography>
                        </Box>
                        
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                          <Typography variant="body2" color="text.secondary">
                            {trade.date}
                          </Typography>
                          <Tooltip title="AI Exit Rationale">
                            <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                              {trade.exitReason}
                            </Typography>
                          </Tooltip>
                        </Box>
                      </Paper>
                    ))}
                  </Box>
                ) : (
                  <Typography variant="body1" sx={{ textAlign: 'center', py: 2 }}>
                    No recent trades to display
                  </Typography>
                )}
              </Paper>
            </Grid>
          </Grid>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 3 }}>
            <FormControlLabel
              control={
                <Switch 
                  checked={showOnStartup}
                  onChange={handleToggleShowOnStartup}
                  color="primary"
                />
              }
              label="Show on startup"
            />
            
            <Button 
              variant="contained" 
              color="primary" 
              onClick={onClose}
              sx={{ fontFamily: 'Orbitron' }}
            >
              Continue to Dashboard
            </Button>
          </Box>
        </Paper>
      </Fade>
    </Modal>
  );
};

const VaultAuth = ({ onAuthenticated }) => {
  const theme = useTheme();
  const [pin, setPin] = useState('');
  const [error, setError] = useState(false);
  const [success, setSuccess] = useState(false);
  const [showMessage, setShowMessage] = useState(false);
  const [message, setMessage] = useState('');
  const [status, setStatus] = useState('idle'); // 'idle', 'loading', 'success', 'error'
  const [attemptCount, setAttemptCount] = useState(0);
  const [audioLoaded, setAudioLoaded] = useState(false);
  const [failedAudio, setFailedAudio] = useState(false);
  const [showStartupModal, setShowStartupModal] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Auto-validate when 4 digits are entered
    if (pin.length === 4) {
      validatePin();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pin]);

  const handlePinChange = (e) => {
    const value = e.target.value;
    // Only allow numbers and max 4 digits
    if (/^\d{0,4}$/.test(value)) {
      setPin(value);
      setError(false);
    }
  };

  const handleKeypadClick = (digit) => {
    if (pin.length < 4) {
      setPin(prev => prev + digit);
    }
  };

  const handleClear = () => {
    setPin('');
    setError(false);
  };

  const validatePin = () => {
    setStatus('loading');
    setShowMessage(true); // Show messages for success/error
    
    // Simulate PIN verification
    setTimeout(() => {
    if (pin === CORRECT_PIN) {
        setStatus('success');
        setSuccess(true); // Set success state for visual alert
        setError(false);
        setMessage('ACCESS GRANTED');
        
        // Show startup modal after successful authentication
        setTimeout(() => {
          // Check if the user has previously disabled the startup modal
          const shouldShowStartupModal = localStorage.getItem('showStartupModal') !== 'false';
          if (shouldShowStartupModal) {
            setShowStartupModal(true);
          } else {
            handleAuthSuccess();
          }
        }, 1500);
    } else {
        // Existing failed authentication logic
        setStatus('error');
        setError(true); // Set error state for visual alert
        setSuccess(false);
        setMessage('ACCESS DENIED');
        setAttemptCount(attemptCount + 1);
        setTimeout(() => {
          setPin('');
          setStatus('idle');
          setMessage('');
          setShowMessage(false); // Hide message after error timeout
        }, 2000);
    }
    }, 1000);
  };

  const handleAuthSuccess = () => {
    // Call the onAuthenticated prop instead of direct navigation
    if (onAuthenticated) {
      onAuthenticated();
    } else {
      // Fallback if onAuthenticated is not provided
      navigate('/dashboard');
    }
  };

  const handleCloseStartupModal = () => {
    setShowStartupModal(false);
    handleAuthSuccess();
  };

  // Create the keypad buttons
  const renderKeypad = () => {
    const keypad = [];
    for (let i = 1; i <= 9; i++) {
      keypad.push(
        <Button 
          key={i}
          onClick={() => handleKeypadClick(i)}
          variant="outlined"
          sx={{
            width: 64,
            height: 64,
            borderRadius: '8px',
            margin: '6px',
            backgroundColor: alpha(theme.palette.primary.main, 0.1),
            color: theme.palette.primary.main,
            fontFamily: 'Share Tech Mono, monospace',
            fontSize: '1.5rem',
            border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
            '&:hover': {
              backgroundColor: alpha(theme.palette.primary.main, 0.2),
              border: `1px solid ${theme.palette.primary.main}`,
            }
          }}
        >
          {i}
        </Button>
      );
    }
    
    // Add 0 button
    keypad.push(
      <Button 
        key={0}
        onClick={() => handleKeypadClick(0)}
        variant="outlined"
        sx={{
          width: 64,
          height: 64,
          borderRadius: '8px',
          margin: '6px',
          backgroundColor: alpha(theme.palette.primary.main, 0.1),
          color: theme.palette.primary.main,
          fontFamily: 'Share Tech Mono, monospace',
          fontSize: '1.5rem',
          border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
          '&:hover': {
            backgroundColor: alpha(theme.palette.primary.main, 0.2),
            border: `1px solid ${theme.palette.primary.main}`,
          }
        }}
      >
        0
      </Button>
    );
    
    return (
      <Box sx={{ 
        display: 'flex', 
        flexWrap: 'wrap', 
        justifyContent: 'center',
        width: 230
      }}>
        {keypad}
      </Box>
    );
  };

  // Futuristic Danger Alert for incorrect PIN
  const renderDangerAlert = () => (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ 
        opacity: 1, 
        scale: 1,
        transition: { 
          duration: 0.3, 
          ease: "easeOut" 
        }
      }}
      exit={{ 
        opacity: 0, 
        scale: 0.9,
        transition: { 
          duration: 0.2, 
          ease: "easeIn" 
        }
      }}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: alpha(theme.palette.error.dark, 0.9),
        zIndex: 10,
        borderRadius: 16,
      }}
    >
      <Box sx={{ 
        textAlign: 'center',
        position: 'relative',
        padding: 3,
      }}>
        {/* Pulsing border effect */}
        <Box
          component={motion.div}
          animate={{ 
            boxShadow: [
              `0 0 0 2px ${alpha(theme.palette.error.main, 0.3)}`,
              `0 0 0 4px ${alpha(theme.palette.error.main, 0.6)}`,
              `0 0 0 2px ${alpha(theme.palette.error.main, 0.3)}`
            ],
          }}
          transition={{ 
            duration: 1.5,
            repeat: Infinity,
            repeatType: "loop"
          }}
          sx={{
            position: 'absolute',
            top: -5,
            left: -5,
            right: -5,
            bottom: -5,
            borderRadius: '50%',
            pointerEvents: 'none',
          }}
        />
        
        <ErrorOutline 
          sx={{ 
            fontSize: 60, 
            color: theme.palette.error.light,
            mb: 2,
            filter: `drop-shadow(0 0 10px ${alpha(theme.palette.error.main, 0.8)})`
          }} 
        />
        
        <Typography 
          variant="h4" 
          sx={{ 
            fontFamily: 'Share Tech Mono, monospace',
            color: theme.palette.error.contrastText,
            fontWeight: 'bold',
            mb: 1,
            textShadow: `0 0 5px ${alpha(theme.palette.error.main, 0.8)}`
          }}
        >
          ACCESS DENIED
        </Typography>
        
        <Typography
          variant="body1"
          sx={{
            fontFamily: 'Share Tech Mono, monospace',
            color: theme.palette.error.contrastText,
          }}
        >
          Security protocol violation detected
        </Typography>
        
        {/* Warning lines */}
        {[...Array(5)].map((_, i) => (
          <Box
            key={i}
            component={motion.div}
            initial={{ width: '20%', opacity: 0.3 }}
            animate={{ 
              width: ['20%', '80%', '20%'],
              opacity: [0.3, 0.8, 0.3],
              x: ['-30%', '0%', '30%']
            }}
            transition={{ 
              duration: 2,
              delay: i * 0.2,
              repeat: Infinity,
              repeatType: "loop"
            }}
            sx={{
              height: '2px',
              backgroundColor: theme.palette.error.light,
              margin: '8px auto',
              borderRadius: '2px',
            }}
          />
        ))}
      </Box>
    </motion.div>
  );

  // Futuristic Initialization Modal for correct PIN
  const renderInitializationModal = () => (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: alpha(theme.palette.primary.dark, 0.95),
        zIndex: 10,
        borderRadius: 16,
        overflow: 'hidden',
      }}
    >
      {/* Moving grid background */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: `linear-gradient(${theme.palette.primary.dark} 1px, transparent 1px), 
                           linear-gradient(90deg, ${theme.palette.primary.dark} 1px, transparent 1px)`,
          backgroundSize: '20px 20px',
          opacity: 0.2,
          animation: 'moveGrid 20s linear infinite',
          '@keyframes moveGrid': {
            '0%': { backgroundPosition: '0 0' },
            '100%': { backgroundPosition: '20px 20px' },
          },
        }}
      />
      
      {/* Loading circle */}
      <Box sx={{ position: 'relative', mb: 4 }}>
        <Box
          component={motion.div}
          animate={{ 
            rotate: 360
          }}
          transition={{ 
            duration: 3,
            repeat: Infinity,
            ease: "linear"
          }}
          sx={{
            width: 100,
            height: 100,
            borderRadius: '50%',
            border: `3px solid transparent`,
            borderTopColor: theme.palette.primary.main,
            borderRightColor: alpha(theme.palette.primary.main, 0.3),
            borderBottomColor: theme.palette.primary.main,
            borderLeftColor: alpha(theme.palette.primary.main, 0.3),
            filter: `drop-shadow(0 0 10px ${alpha(theme.palette.primary.main, 0.8)})`
          }}
        />
        
        <CheckCircleOutline
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            fontSize: 40,
            color: theme.palette.primary.light,
          }}
        />
      </Box>
      
      <Typography 
        variant="h4" 
        sx={{ 
          fontFamily: 'Share Tech Mono, monospace',
          color: theme.palette.primary.contrastText,
          fontWeight: 'bold',
          mb: 2,
          textShadow: `0 0 10px ${alpha(theme.palette.primary.main, 0.8)}`
        }}
      >
        ACCESS GRANTED
      </Typography>
      
      {/* Simulated system initialization */}
      <Box sx={{ width: '80%', maxWidth: 300 }}>
        {['System', 'Protocols', 'Security', 'Interface', 'Database'].map((item, index) => (
          <Box key={index} sx={{ mb: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography 
                variant="body2" 
                sx={{ 
                  fontFamily: 'Share Tech Mono, monospace',
                  color: theme.palette.primary.contrastText,
                }}
              >
                {item}
              </Typography>
              
              <Typography 
                component={motion.div}
                initial={{ opacity: 0 }}
                animate={{ 
                  opacity: 1,
                  transition: { delay: 0.5 + (index * 0.2) }
                }}
                variant="body2" 
                sx={{ 
                  fontFamily: 'Share Tech Mono, monospace',
                  color: theme.palette.primary.light, 
                }}
              >
                INITIALIZED
              </Typography>
            </Box>
            
            <Box 
              component={motion.div}
              initial={{ width: '0%' }}
              animate={{ 
                width: '100%',
                transition: { 
                  duration: 0.5, 
                  delay: 0.2 + (index * 0.2) 
                }
              }}
              sx={{ 
                height: '4px', 
                backgroundColor: theme.palette.primary.main,
                borderRadius: '2px',
                boxShadow: `0 0 5px ${theme.palette.primary.main}`
              }} 
            />
          </Box>
        ))}
      </Box>
    </motion.div>
  );

  return (
    <>
      <MotionConfig>
        <AnimatePresence mode="wait">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: alpha(theme.palette.background.default, 0.85),
              backdropFilter: 'blur(8px)',
              zIndex: 1300,
            }}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ type: 'spring', damping: 20, stiffness: 100 }}
            >
              <Paper
                elevation={24}
                sx={{
                  padding: 4,
                  borderRadius: 4,
                  maxWidth: 400,
                  width: '100%',
                  backgroundColor: alpha(theme.palette.background.paper, 0.9),
                  border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                {/* Animated glowing background */}
                <Box
                  sx={{
                    position: 'absolute',
                    top: '-50%',
                    left: '-50%',
                    right: '-50%',
                    bottom: '-50%',
                    background: `radial-gradient(circle, ${alpha(theme.palette.primary.main, 0.1)} 0%, transparent 70%)`,
                    animation: 'pulse 3s infinite ease-in-out',
                    '@keyframes pulse': {
                      '0%': { opacity: 0.3, transform: 'scale(0.9)' },
                      '50%': { opacity: 0.6, transform: 'scale(1.1)' },
                      '100%': { opacity: 0.3, transform: 'scale(0.9)' },
                    },
                  }}
                />
                
                <Box sx={{ position: 'relative', zIndex: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 3 }}>
                    <motion.div
                      animate={{ rotate: [0, 360] }}
                      transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
                    >
                      <Lock 
                        sx={{ 
                          fontSize: 48, 
                          color: error ? theme.palette.error.main : 
                                 success ? theme.palette.success.main : 
                                 theme.palette.primary.main,
                          mr: 2 
                        }} 
                      />
                    </motion.div>
                    <Typography 
                      variant="h4" 
                      component="h1" 
                      fontFamily="Share Tech Mono, monospace"
                      color={theme.palette.primary.main}
                      sx={{ textShadow: `0 0 8px ${alpha(theme.palette.primary.main, 0.5)}` }}
                    >
                      VAULT ACCESS
                    </Typography>
                  </Box>
                  
                  <Typography 
                    align="center" 
                    variant="subtitle1" 
                    mb={3}
                    fontFamily="Share Tech Mono, monospace"
                    color={theme.palette.text.secondary}
                    sx={{ 
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: 1
                    }}
                  >
                    <Fingerprint color="primary" />
                    Enter 4-Digit Security PIN
                  </Typography>
                  
                  {/* PIN Display */}
                  <Box sx={{ mb: 3, position: 'relative' }}>
                    <TextField
                      fullWidth
                      variant="outlined"
                      type="password"
                      value={pin}
                      onChange={handlePinChange}
                      inputProps={{ 
                        maxLength: 4,
                        style: { 
                          textAlign: 'center',
                          fontFamily: 'Share Tech Mono, monospace',
                          fontSize: '2rem',
                          letterSpacing: '1rem',
                          color: error ? theme.palette.error.main : 
                                 success ? theme.palette.success.main : 
                                 theme.palette.primary.main
                        } 
                      }}
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          '& fieldset': {
                            borderColor: error ? theme.palette.error.main : 
                                        success ? theme.palette.success.main : 
                                        alpha(theme.palette.primary.main, 0.5),
                            borderWidth: 2,
                            borderRadius: 2
                          },
                          '&:hover fieldset': {
                            borderColor: error ? theme.palette.error.main : 
                                        success ? theme.palette.success.main : 
                                        theme.palette.primary.main
                          },
                          '&.Mui-focused fieldset': {
                            borderColor: error ? theme.palette.error.main : 
                                        success ? theme.palette.success.main : 
                                        theme.palette.primary.main
                          }
                        }
                      }}
                    />
                    
                    {/* Digital display showing PIN as dots */}
                    <Box 
                      sx={{ 
                        position: 'absolute', 
                        top: '50%', 
                        left: 0, 
                        right: 0, 
                        transform: 'translateY(-50%)',
                        display: 'flex',
                        justifyContent: 'center',
                        gap: 2,
                        pointerEvents: 'none'
                      }}
                    >
                      {[...Array(4)].map((_, index) => (
                        <Box 
                          key={index}
                          sx={{
                            width: 20,
                            height: 20,
                            borderRadius: '50%',
                            backgroundColor: pin.length > index 
                              ? error 
                                ? theme.palette.error.main 
                                : success 
                                  ? theme.palette.success.main 
                                  : theme.palette.primary.main
                              : 'transparent',
                            border: `2px solid ${
                              error 
                                ? alpha(theme.palette.error.main, 0.5) 
                                : success 
                                  ? alpha(theme.palette.success.main, 0.5) 
                                  : alpha(theme.palette.primary.main, 0.5)
                            }`,
                            transition: 'all 0.2s ease'
                          }}
                        />
                      ))}
                    </Box>
                  </Box>
                  
                  {/* Keypad */}
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                    {renderKeypad()}
                    
                    <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                      <Button 
                        variant="outlined" 
                        color="error" 
                        onClick={handleClear}
                        sx={{ 
                          width: 140,
                          fontFamily: 'Share Tech Mono, monospace',
                          borderRadius: 2
                        }}
                      >
                        CLEAR
                      </Button>
                    </Box>
                  </Box>
                  
                  {/* Visual alerts */}
                  <AnimatePresence>
                    {error && showMessage && renderDangerAlert()}
                    {success && showMessage && renderInitializationModal()}
                  </AnimatePresence>
                </Box>
              </Paper>
            </motion.div>
          </motion.div>
        </AnimatePresence>
      </MotionConfig>
      
      {/* Add the StartupIntelligenceModal */}
      <StartupIntelligenceModal 
        open={showStartupModal} 
        onClose={handleCloseStartupModal}
      />
    </>
  );
};

export default VaultAuth; 