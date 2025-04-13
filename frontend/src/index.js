import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';
import App from './App';
import { NotificationProvider } from './contexts/NotificationContext';
import './index.css';

// Enable debugging for troubleshooting
const DEBUG = process.env.NODE_ENV === 'development';
if (DEBUG) {
  console.log('Running in development mode with debug enabled');
}

// Global ResizeObserver error handler to prevent console errors
if (typeof window !== 'undefined') {
  // Prevent ResizeObserver loop limit exceeded errors from breaking the app
  const originalConsoleError = console.error;
  console.error = (...args) => {
    if (
      args[0]?.includes?.('ResizeObserver loop limit exceeded') ||
      args[0]?.includes?.('ResizeObserver loop completed with undelivered notifications')
    ) {
      // Just ignore these specific errors
      return;
    }
    originalConsoleError(...args);
  };

  // Global error handler for ResizeObserver errors
  window.addEventListener('error', (event) => {
    if (
      event.message === 'ResizeObserver loop limit exceeded' ||
      event.message.includes('ResizeObserver loop completed with undelivered notifications')
    ) {
      event.stopImmediatePropagation();
      event.preventDefault();
      return false;
    }
  });
}

// Render the application
ReactDOM.render(
  <React.StrictMode>
    <NotificationProvider>
      <Router>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <App />
        </ThemeProvider>
      </Router>
    </NotificationProvider>
  </React.StrictMode>,
  document.getElementById('root')
); 