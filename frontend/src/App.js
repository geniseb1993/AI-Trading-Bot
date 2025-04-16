import React, { useContext } from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import LiveMarket from './pages/LiveMarket';
import Signals from './pages/Signals';
import Backtest from './pages/Backtest';
import MarketData from './pages/MarketData';
import TradingViewAlerts from './pages/TradingViewAlerts';
import APIConfiguration from './pages/APIConfiguration';
import MarketAnalysis from './pages/MarketAnalysis';
import InstitutionalFlow from './pages/InstitutionalFlow';
import TradeSetups from './pages/TradeSetups';
import Settings from './pages/Settings';
import RiskManagement from './pages/RiskManagement';
import BotManagement from './pages/BotManagement';
import Debug from './pages/Debug';
import { Button } from '@mui/material';
import NotificationContext from './contexts/NotificationContext';

function App() {
  const { addNotification, sendVoiceNotification } = useContext(NotificationContext) || {};
  
  const testDesktopNotification = () => {
    if (!addNotification) {
      console.error("Notification context not available");
      return;
    }
    
    console.log("Testing notification from App");
    
    const notification = {
      id: Date.now(),
      type: 'test',
      title: 'Trading Opportunity',
      message: 'AAPL bullish signal detected at $195.67',
      data: { symbol: 'AAPL', price: 195.67, action: 'BUY' },
      priority: 'high',
      group: 'trade',
      timestamp: new Date().toISOString(),
      read: false
    };
    
    // Add the notification
    addNotification(notification);
    
    // Also test voice notification
    if (sendVoiceNotification) {
      console.log("Testing voice notification from App");
      sendVoiceNotification({
        ...notification,
        message: "This is a test of the Hume AI voice notification system for a trading opportunity on Apple stock at $195.67. If you're hearing this in a natural voice, it's working correctly."
      });
    }
  };

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/live-market" element={<LiveMarket />} />
        <Route path="/signals" element={<Signals />} />
        <Route path="/backtest" element={<Backtest />} />
        <Route path="/market-data" element={<MarketData />} />
        <Route path="/tradingview-alerts" element={<TradingViewAlerts />} />
        <Route path="/market-data-config" element={<APIConfiguration />} />
        <Route path="/market-analysis" element={<MarketAnalysis />} />
        <Route path="/institutional-flow" element={<InstitutionalFlow />} />
        <Route path="/trade-setups" element={<TradeSetups />} />
        <Route path="/risk-management" element={<RiskManagement />} />
        <Route path="/bot-management" element={<BotManagement />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/debug" element={<Debug />} />
      </Routes>
      
      <Button 
        variant="contained" 
        color="primary" 
        onClick={testDesktopNotification}
        style={{ 
          position: 'fixed', 
          bottom: '20px', 
          right: '20px',
          zIndex: 9999 
        }}
      >
        Test Trading Alert
      </Button>
    </Layout>
  );
}

export default App; 