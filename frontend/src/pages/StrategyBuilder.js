import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Stepper, 
  Step, 
  StepLabel, 
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Chip,
  IconButton,
  Alert,
  Snackbar,
  Divider,
  useTheme,
  Tooltip,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import { motion } from 'framer-motion';
import { 
  Add, 
  Delete, 
  Edit, 
  Check, 
  Save, 
  PlayArrow, 
  Code, 
  Settings,
  ExpandMore,
  ChevronRight,
  Close,
  Info
} from '@mui/icons-material';
import ReactFlow, { 
  Background, 
  Controls, 
  MiniMap, 
  addEdge, 
  useNodesState, 
  useEdgesState 
} from 'reactflow';
import 'reactflow/dist/style.css';
import axios from 'axios';

// Import our new layout components
import PageLayout from '../components/PageLayout';
import ContentCard from '../components/ContentCard';
import ContentGrid from '../components/ContentGrid';

// Import custom nodes & components
import IndicatorNode from '../components/nodes/IndicatorNode';
import ConditionNode from '../components/nodes/ConditionNode';
import ActionNode from '../components/nodes/ActionNode';
import SignalNode from '../components/nodes/SignalNode';
import StrategyForm from '../components/strategy/StrategyForm';
import BacktestForm from '../components/strategy/BacktestForm';
import CodeViewer from '../components/CodeViewer';

// Node types for ReactFlow
const nodeTypes = {
  indicatorNode: IndicatorNode,
  conditionNode: ConditionNode,
  actionNode: ActionNode,
  signalNode: SignalNode
};

const steps = ['Strategy Details', 'Build Logic', 'Backtest', 'Deploy'];

const StrategyBuilder = () => {
  const theme = useTheme();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [strategyName, setStrategyName] = useState('');
  const [description, setDescription] = useState('');
  const [timeframe, setTimeframe] = useState('1h');
  const [symbols, setSymbols] = useState(['BTCUSDT']);
  const [symbolInput, setSymbolInput] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [backtestResults, setBacktestResults] = useState(null);
  const [showCode, setShowCode] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');
  const [formErrors, setFormErrors] = useState({});
  
  // React Flow state
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  
  useEffect(() => {
    // Initial nodes setup
    const initialNodes = [
      {
        id: 'signal-1',
        type: 'signalNode',
        data: { label: 'Signal' },
        position: { x: 400, y: 400 }
      }
    ];
    
    setNodes(initialNodes);
  }, []);
  
  const handleConnect = (params) => {
    setEdges((eds) => addEdge(params, eds));
  };
  
  const addNode = (type) => {
    let nodeData = {};
    let label = '';
    
    switch(type) {
      case 'indicator':
        label = 'New Indicator';
        nodeData = { 
          type: 'RSI', 
          params: { period: 14 },
          label: 'RSI (14)'
        };
        break;
      case 'condition':
        label = 'New Condition';
        nodeData = {
          operator: '>',
          value: 70,
          label: '> 70'
        };
        break;
      case 'action':
        label = 'New Action';
        nodeData = {
          type: 'BUY',
          params: { amount: '100%' },
          label: 'BUY 100%'
        };
        break;
      default:
        label = 'New Node';
    }
    
    const newNode = {
      id: `${type}-${Date.now()}`,
      type: `${type}Node`,
      data: { label: label, ...nodeData },
      position: {
        x: Math.random() * 400 + 100,
        y: Math.random() * 400 + 100,
      },
    };
    
    setNodes((nds) => nds.concat(newNode));
  };
  
  const handleNext = () => {
    if (activeStep === 0) {
      // Validate first step
      const errors = {};
      if (!strategyName.trim()) errors.strategyName = 'Strategy name is required';
      if (!description.trim()) errors.description = 'Description is required';
      if (symbols.length === 0) errors.symbols = 'At least one symbol is required';
      
      if (Object.keys(errors).length > 0) {
        setFormErrors(errors);
        return;
      }
      
      setFormErrors({});
    }
    
    if (activeStep === 1) {
      // Generate code from flow
      const strategyCode = generateCodeFromFlow();
      setGeneratedCode(strategyCode);
    }
    
    if (activeStep === 2) {
      // Run backtest
      runBacktest();
    }
    
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };
  
  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };
  
  const handleSymbolAdd = () => {
    if (symbolInput && !symbols.includes(symbolInput.toUpperCase())) {
      setSymbols([...symbols, symbolInput.toUpperCase()]);
      setSymbolInput('');
    }
  };
  
  const handleSymbolDelete = (symbolToDelete) => {
    setSymbols(symbols.filter((symbol) => symbol !== symbolToDelete));
  };
  
  const generateCodeFromFlow = () => {
    // Mock code generation
    const code = `
// Auto-generated strategy code
import { Strategy, RSI, EMA, MACD } from 'trading-engine';

class ${strategyName.replace(/\s+/g, '')} extends Strategy {
  constructor() {
    super({
      name: "${strategyName}",
      description: "${description}",
      timeframe: "${timeframe}",
      symbols: ${JSON.stringify(symbols)}
    });
    
    // Initialize indicators
    this.rsi = new RSI(14);
    this.ema = new EMA(200);
    
    // Init state
    this.lastSignal = null;
  }
  
  async onTick(candle) {
    // Update indicators
    this.rsi.update(candle.close);
    this.ema.update(candle.close);
    
    // Strategy logic
    if (candle.close > this.ema.value && this.rsi.value < 30) {
      if (this.lastSignal !== 'buy') {
        this.buy({ amount: '100%' });
        this.lastSignal = 'buy';
      }
    } else if (candle.close < this.ema.value && this.rsi.value > 70) {
      if (this.lastSignal !== 'sell') {
        this.sell({ amount: '100%' });
        this.lastSignal = 'sell';
      }
    }
  }
}

export default ${strategyName.replace(/\s+/g, '')};
`;
    
    return code;
  };
  
  const runBacktest = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Mock API call for backtest
      // const response = await axios.post('/api/backtest', {
      //   strategy: strategyName,
      //   code: generatedCode,
      //   timeframe,
      //   symbols,
      //   period: '3mo' // Last 3 months
      // });
      
      // Mock response
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockResults = {
        performance: {
          totalReturns: 28.4,
          maxDrawdown: 12.5,
          sharpeRatio: 1.8,
          winRate: 65.2,
          totalTrades: 48
        },
        trades: Array.from({ length: 20 }, (_, i) => ({
          id: `trade-${i+1}`,
          symbol: symbols[Math.floor(Math.random() * symbols.length)],
          side: Math.random() > 0.5 ? 'BUY' : 'SELL',
          entryPrice: 20000 + Math.random() * 10000,
          exitPrice: 20000 + Math.random() * 10000,
          entryTime: new Date(Date.now() - Math.random() * 7776000000).toISOString(), // within 90 days
          exitTime: new Date(Date.now() - Math.random() * 2592000000).toISOString(), // within 30 days
          profit: Math.random() > 0.3 ? Math.random() * 500 : -Math.random() * 300,
          profitPercent: Math.random() > 0.3 ? Math.random() * 5 : -Math.random() * 3,
        })),
        equity: Array.from({ length: 90 }, (_, i) => {
          const date = new Date();
          date.setDate(date.getDate() - (89 - i));
          return {
            date: date.toISOString().split('T')[0],
            value: 10000 * (1 + 0.284 * (i/89)) + (Math.random() - 0.5) * 500
          };
        })
      };
      
      setBacktestResults(mockResults);
      setSuccess("Backtest completed successfully!");
    } catch (err) {
      console.error('Backtest error:', err);
      setError(err.response?.data?.message || 'Failed to run backtest');
    } finally {
      setLoading(false);
    }
  };
  
  const deployStrategy = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Mock API call for deployment
      // const response = await axios.post('/api/strategies/deploy', {
      //   name: strategyName,
      //   code: generatedCode,
      //   timeframe,
      //   symbols
      // });
      
      // Mock response
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setSuccess("Strategy deployed successfully!");
    } catch (err) {
      console.error('Deployment error:', err);
      setError(err.response?.data?.message || 'Failed to deploy strategy');
    } finally {
      setLoading(false);
    }
  };
  
  const handleCloseAlert = () => {
    setSuccess(null);
    setError(null);
  };
  
  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <StrategyForm 
            strategyName={strategyName}
            setStrategyName={setStrategyName}
            description={description}
            setDescription={setDescription}
            timeframe={timeframe}
            setTimeframe={setTimeframe}
            symbols={symbols}
            symbolInput={symbolInput}
            setSymbolInput={setSymbolInput}
            handleSymbolAdd={handleSymbolAdd}
            handleSymbolDelete={handleSymbolDelete}
            formErrors={formErrors}
          />
        );
      case 1:
        return (
          <Box sx={{ height: '600px', width: '100%' }}>
            <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
              <Button 
                variant="outlined" 
                color="primary" 
                startIcon={<Add />}
                onClick={() => addNode('indicator')}
              >
                Add Indicator
              </Button>
              <Button 
                variant="outlined" 
                color="primary" 
                startIcon={<Add />}
                onClick={() => addNode('condition')}
              >
                Add Condition
              </Button>
              <Button 
                variant="outlined" 
                color="primary" 
                startIcon={<Add />}
                onClick={() => addNode('action')}
              >
                Add Action
              </Button>
              <Button 
                variant="outlined" 
                color="secondary" 
                startIcon={<Code />}
                onClick={() => setShowCode(!showCode)}
              >
                {showCode ? 'Hide Code' : 'View Code'}
              </Button>
            </Box>
            
            {showCode ? (
              <CodeViewer 
                code={generateCodeFromFlow()} 
                language="javascript" 
                height="530px" 
              />
            ) : (
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={handleConnect}
                nodeTypes={nodeTypes}
                fitView
              >
                <Controls />
                <MiniMap />
                <Background variant="dots" gap={12} size={1} />
              </ReactFlow>
            )}
          </Box>
        );
      case 2:
        return (
          <BacktestForm 
            strategyName={strategyName}
            symbols={symbols}
            timeframe={timeframe}
            onRunBacktest={runBacktest}
            results={backtestResults}
            loading={loading}
          />
        );
      case 3:
        return (
          <Box>
            <Typography variant="h6" sx={{ mb: 3 }}>Strategy Summary</Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" fontWeight="bold">Name:</Typography>
                <Typography paragraph>{strategyName}</Typography>
                
                <Typography variant="subtitle1" fontWeight="bold">Description:</Typography>
                <Typography paragraph>{description}</Typography>
                
                <Typography variant="subtitle1" fontWeight="bold">Time Frame:</Typography>
                <Typography paragraph>{timeframe}</Typography>
                
                <Typography variant="subtitle1" fontWeight="bold">Symbols:</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                  {symbols.map((symbol) => (
                    <Chip key={symbol} label={symbol} />
                  ))}
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" fontWeight="bold">Backtest Performance:</Typography>
                {backtestResults ? (
                  <Box>
                    <Typography>Total Return: {backtestResults.performance.totalReturns.toFixed(2)}%</Typography>
                    <Typography>Win Rate: {backtestResults.performance.winRate.toFixed(2)}%</Typography>
                    <Typography>Sharpe Ratio: {backtestResults.performance.sharpeRatio.toFixed(2)}</Typography>
                    <Typography>Max Drawdown: {backtestResults.performance.maxDrawdown.toFixed(2)}%</Typography>
                    <Typography>Total Trades: {backtestResults.performance.totalTrades}</Typography>
                  </Box>
                ) : (
                  <Typography color="text.secondary">No backtest data available</Typography>
                )}
              </Grid>
            </Grid>
            
            <Box sx={{ mt: 4 }}>
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body1">
                  Once deployed, your strategy will start trading automatically according to the defined rules.
                  You can monitor its performance and pause it at any time from the Strategy Management page.
                </Typography>
              </Alert>
              
              <Button
                variant="contained"
                color="primary"
                onClick={deployStrategy}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
              >
                Deploy Strategy
              </Button>
            </Box>
          </Box>
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <PageLayout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography 
          variant="h4" 
          component={motion.h4}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          sx={{ 
            fontWeight: 'bold',
            color: 'primary.main'
          }}
        >
          Strategy Builder
        </Typography>
      </Box>

      <ContentGrid>
        <Grid item xs={12}>
          <ContentCard>
            <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
            
            <Box>
              {getStepContent(activeStep)}
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                <Button
                  variant="outlined"
                  disabled={activeStep === 0}
                  onClick={handleBack}
                >
                  Back
                </Button>
                <Box>
                  {activeStep === steps.length - 1 ? (
                    <Button 
                      variant="contained" 
                      color="primary" 
                      onClick={deployStrategy}
                      disabled={loading}
                      startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
                    >
                      Deploy
                    </Button>
                  ) : (
                    <Button 
                      variant="contained" 
                      color="primary" 
                      onClick={handleNext}
                    >
                      Next
                    </Button>
                  )}
                </Box>
              </Box>
            </Box>
          </ContentCard>
        </Grid>
      </ContentGrid>
      
      <Snackbar open={!!success || !!error} autoHideDuration={6000} onClose={handleCloseAlert}>
        <Alert 
          onClose={handleCloseAlert} 
          severity={success ? 'success' : 'error'} 
          sx={{ width: '100%' }}
        >
          {success || error}
        </Alert>
      </Snackbar>
    </PageLayout>
  );
};

export default StrategyBuilder; 