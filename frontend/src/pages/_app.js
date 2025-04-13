import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from '../theme';
import Layout from '../components/Layout';
import { NotificationProvider } from '../contexts/NotificationContext';
import '../styles/globals.css';

function MyApp({ Component, pageProps }) {
  return (
    <NotificationProvider>
      <Router>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Layout>
            <Component {...pageProps} />
          </Layout>
        </ThemeProvider>
      </Router>
    </NotificationProvider>
  );
}

export default MyApp; 