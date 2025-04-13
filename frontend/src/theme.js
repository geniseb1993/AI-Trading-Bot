import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#0ae0ec',
      light: '#22f2ff',
      dark: '#057078',
    },
    secondary: {
      main: '#6e44ff',
      light: '#9c7dff',
      dark: '#4d2db7',
    },
    background: {
      default: '#0a0e17',
      paper: '#12172b',
    },
    text: {
      primary: '#e0e0f0',
      secondary: '#a0a0b8',
    },
    error: {
      main: '#ff3d71',
    },
    success: {
      main: '#00e096',
    },
    warning: {
      main: '#ffaa00',
    },
    info: {
      main: '#00d4ff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontFamily: '"Orbitron", sans-serif',
    },
    h2: {
      fontFamily: '"Orbitron", sans-serif',
    },
    h3: {
      fontFamily: '"Orbitron", sans-serif',
    },
    h4: {
      fontFamily: '"Orbitron", sans-serif',
    },
    h5: {
      fontFamily: '"Orbitron", sans-serif',
    },
    h6: {
      fontFamily: '"Orbitron", sans-serif',
    },
    button: {
      fontFamily: '"Orbitron", sans-serif',
      fontWeight: 500,
      letterSpacing: '0.1em',
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#12172b',
          border: '1px solid rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-5px)',
            boxShadow: '0 8px 30px rgba(0, 0, 0, 0.7), 0 0 10px #057078',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          textTransform: 'uppercase',
          fontWeight: 500,
          letterSpacing: '0.1em',
          position: 'relative',
          overflow: 'hidden',
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: '0 0 15px #0ae0ec',
          },
          '&:active': {
            transform: 'scale(0.98)',
          },
        },
      },
    },
  },
});

export default theme; 