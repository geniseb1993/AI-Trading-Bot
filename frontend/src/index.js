import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter as Router } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';
import App from './App';
import { NotificationProvider } from './contexts/NotificationContext';
import './index.css';
import reportWebVitals from './reportWebVitals';

// Handle ResizeObserver errors
const originalConsoleError = console.error;
console.error = function(msg) {
  if (typeof msg === 'string' && msg.includes('ResizeObserver')) {
    // Ignore ResizeObserver errors
    return;
  }
  originalConsoleError.apply(console, arguments);
};

// Create root with React 18 API
const container = document.getElementById('root');
const root = createRoot(container);

// Render application
root.render(
  <React.StrictMode>
    <NotificationProvider>
      <Router>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <App />
        </ThemeProvider>
      </Router>
    </NotificationProvider>
  </React.StrictMode>
);

// Report web vitals
reportWebVitals(); 