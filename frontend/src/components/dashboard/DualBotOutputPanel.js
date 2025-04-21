import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Divider,
  Chip,
  Grid,
  CircularProgress,
  Button,
  useTheme,
  alpha,
  Paper,
  List,
  ListItem,
  ListItemText,
  Alert
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Refresh,
  BarChart,
  CheckCircle,
  Warning,
  Info
} from '@mui/icons-material';
import apiService from '../../services/apiService';

/**
 * DualBotOutputPanel component displays the output of the Dual Bot system
 * including trade recommendations and risk assessments
 */
const DualBotOutputPanel = ({ botData = {}, onRefresh }) => {
  const theme = useTheme();
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [riskAssessments, setRiskAssessments] = useState([]);
  const [error, setError] = useState(null);
  const [lastFetched, setLastFetched] = useState(null);

  useEffect(() => {
    fetchData();
    // Set up polling every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Try to load recommendations from API
      const recommendationsResponse = await apiService.apiRequest(
        '/api/dual-bot/recommendations',
        'GET',
        {},
        true
      );
      
      // Try to load risk assessments from API
      const riskResponse = await apiService.apiRequest(
        '/api/dual-bot/risk-assessments',
        'GET',
        {},
        true
      );
      
      if (recommendationsResponse.data && recommendationsResponse.data.recommendations) {
        setRecommendations(recommendationsResponse.data.recommendations);
      }
      
      if (riskResponse.data && riskResponse.data.assessments) {
        setRiskAssessments(riskResponse.data.assessments);
      }
      
      setLastFetched(new Date());
      setError(null);
    } catch (err) {
      console.error('Error fetching dual bot data:', err);
      setError('Failed to fetch bot data. Using sample data instead.');
      
      // Use sample data if API fails
      const sampleRecommendations = [
        {
          symbol: 'AAPL',
          direction: 'bullish',
          confidence: 0.85,
          entry_price: 190.0,
          stop_loss: 185.0,
          take_profit: 200.0,
          timestamp: new Date().toISOString(),
          reasoning: 'Strong momentum and positive market sentiment. Price above key moving averages with increasing volume.'
        },
        {
          symbol: 'TSLA',
          direction: 'bearish',
          confidence: 0.75,
          entry_price: 215.5,
          stop_loss: 225.0,
          take_profit: 200.0,
          timestamp: new Date().toISOString(),
          reasoning: 'Weakening momentum with bearish divergence on RSI. Recent resistance at 225 level.'
        }
      ];
      
      const sampleRiskAssessments = [
        {
          symbol: 'AAPL',
          approved: true,
          confidence: 0.8,
          risk_level: 'MEDIUM',
          timestamp: new Date().toISOString(),
          reason: 'Acceptable risk profile with strong technical indicators, though market volatility remains a concern.'
        },
        {
          symbol: 'TSLA',
          approved: false,
          confidence: 0.6,
          risk_level: 'HIGH',
          timestamp: new Date().toISOString(),
          reason: 'High market volatility and uncertain news sentiment suggest waiting for better entry point.'
        }
      ];
      
      setRecommendations(sampleRecommendations);
      setRiskAssessments(sampleRiskAssessments);
      setLastFetched(new Date());
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchData();
    if (onRefresh) onRefresh();
  };

  const renderRecommendation = (recommendation, index) => {
    const isBullish = recommendation.direction === 'bullish';
    const backgroundColor = alpha(
      isBullish ? theme.palette.success.main : theme.palette.error.main,
      0.1
    );
    
    // Find matching risk assessment if any
    const matchingAssessment = riskAssessments.find(
      assessment => assessment.symbol === recommendation.symbol
    );
    
    return (
      <Paper
        key={`${recommendation.symbol}-${index}`}
        elevation={1}
        sx={{
          mb: 2,
          p: 2,
          backgroundColor,
          borderLeft: `4px solid ${isBullish ? theme.palette.success.main : theme.palette.error.main}`
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            {recommendation.symbol}
          </Typography>
          <Chip
            icon={isBullish ? <TrendingUp /> : <TrendingDown />}
            label={isBullish ? 'BUY' : 'SELL'}
            color={isBullish ? 'success' : 'error'}
            size="small"
          />
        </Box>
        
        <Grid container spacing={1} sx={{ mb: 1 }}>
          <Grid item xs={4}>
            <Typography variant="caption" color="text.secondary">
              Entry Price
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
              ${recommendation.entry_price?.toFixed(2)}
            </Typography>
          </Grid>
          <Grid item xs={4}>
            <Typography variant="caption" color="text.secondary">
              Stop Loss
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
              ${recommendation.stop_loss?.toFixed(2)}
            </Typography>
          </Grid>
          <Grid item xs={4}>
            <Typography variant="caption" color="text.secondary">
              Target
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
              ${recommendation.take_profit?.toFixed(2)}
            </Typography>
          </Grid>
        </Grid>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Confidence: {(recommendation.confidence * 100).toFixed(0)}%
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {new Date(recommendation.timestamp).toLocaleTimeString()}
          </Typography>
        </Box>
        
        <Typography variant="body2" sx={{ fontSize: '0.75rem', fontStyle: 'italic' }}>
          {recommendation.reasoning}
        </Typography>
        
        {matchingAssessment && (
          <Box sx={{ mt: 1, pt: 1, borderTop: `1px dashed ${theme.palette.divider}` }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                Risk Assessment
              </Typography>
              <Chip
                icon={matchingAssessment.approved ? <CheckCircle /> : <Warning />}
                label={matchingAssessment.approved ? 'APPROVED' : 'REJECTED'}
                color={matchingAssessment.approved ? 'success' : 'warning'}
                size="small"
                sx={{ height: 20, '& .MuiChip-label': { px: 1, py: 0 } }}
              />
            </Box>
            <Typography 
              variant="caption" 
              color={
                matchingAssessment.risk_level === 'LOW' ? 'success.main' :
                matchingAssessment.risk_level === 'MEDIUM' ? 'warning.main' : 'error.main'
              }
            >
              {matchingAssessment.risk_level} RISK ({(matchingAssessment.confidence * 100).toFixed(0)}% confidence)
            </Typography>
            <Typography variant="body2" sx={{ fontSize: '0.7rem', mt: 0.5 }}>
              {matchingAssessment.reason}
            </Typography>
          </Box>
        )}
      </Paper>
    );
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
            <BarChart sx={{ mr: 1 }} />
            Dual Bot Output
          </Typography>
          <Button
            size="small"
            startIcon={<Refresh />}
            onClick={handleRefresh}
            disabled={loading}
            variant="outlined"
          >
            Refresh
          </Button>
        </Box>
        
        {error && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Box sx={{ flexGrow: 1, overflow: 'auto', maxHeight: 'calc(100vh - 300px)' }}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress size={30} />
            </Box>
          ) : recommendations.length > 0 ? (
            recommendations.map(renderRecommendation)
          ) : (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Info color="disabled" sx={{ fontSize: 40, mb: 1 }} />
              <Typography color="text.secondary">
                No trade recommendations available
              </Typography>
            </Box>
          )}
        </Box>
        
        {lastFetched && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, textAlign: 'right' }}>
            Last updated: {lastFetched.toLocaleTimeString()}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default DualBotOutputPanel; 