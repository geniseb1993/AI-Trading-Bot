import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter as Router } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';
import App from './App';
import { NotificationProvider } from './contexts/NotificationContext';
import { DataProvider } from './contexts/DataContext';
import './index.css';
import reportWebVitals from './reportWebVitals';

// Handle ResizeObserver errors and improve error logging
const originalConsoleError = console.error;
console.error = function(msg, ...args) {
  // Ignore ResizeObserver errors
  if (typeof msg === 'string' && msg.includes('ResizeObserver')) {
    return;
  }
  
  // Filter out 404 errors for GPT insights to avoid console spam
  if (typeof msg === 'string' && (
      msg.includes('Error fetching GPT insights') || 
      msg.includes('Failed to load resource: the server responded with a status of 404')
    )) {
    // Log a cleaner message once
    if (!window.loggedGptError) {
      originalConsoleError.call(console, 'GPT insights API not available (expected in development mode)');
      window.loggedGptError = true;
    }
    return;
  }
  
  // For all other errors, pass through to original handler
  originalConsoleError.apply(console, [msg, ...args]);
};

// Create root with React 18 API
const container = document.getElementById('root');
const root = createRoot(container);

// Render application
root.render(
  <React.StrictMode>
    <NotificationProvider>
      <DataProvider>
      <Router>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <App />
        </ThemeProvider>
      </Router>
      </DataProvider>
    </NotificationProvider>
  </React.StrictMode>
);

// Report web vitals
reportWebVitals(); 