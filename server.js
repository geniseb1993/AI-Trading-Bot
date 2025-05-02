// Simple Express server to bind to PORT for Render detection
// This is a fallback in case Render tries to run Node.js instead of Python

const express = require('express');
const { spawn } = require('child_process');
const app = express();
const port = process.env.PORT || 10000;

console.log('Starting fallback server.js');
console.log('This application should be run as a Python application, not Node.js');
console.log('Attempting to start Python application in the background...');

// Try to start the Python app in the background
try {
  const pythonApp = spawn('bash', ['-c', '. .venv/bin/activate && gunicorn wsgi:app --bind=0.0.0.0:8000'], {
    stdio: 'inherit'
  });

  pythonApp.on('error', (err) => {
    console.error('Error starting Python app:', err);
  });
} catch (err) {
  console.error('Failed to start Python app:', err);
}

// Simple health check endpoint
app.get('/health', (req, res) => {
  res.send({ status: 'ok', message: 'Node.js fallback server is running' });
});

// Root endpoint with information
app.get('/', (req, res) => {
  res.send(`
    <html>
      <head>
        <title>AI Trading Bot - Fallback Server</title>
        <style>
          body { font-family: sans-serif; margin: 0; padding: 20px; background: #121212; color: #e1e1e1; }
          .container { max-width: 800px; margin: 40px auto; padding: 20px; background: #1e1e1e; border-radius: 8px; }
          h1 { color: #4a90e2; }
          pre { background: #2d2d2d; padding: 15px; border-radius: 4px; overflow-x: auto; }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>AI Trading Bot - Node.js Fallback Server</h1>
          <p>This is a fallback server. The application should be running as a Python application.</p>
          <p>Please check Render logs for more information.</p>
          
          <h2>Environment Information:</h2>
          <pre>PORT: ${process.env.PORT || 'Not set'}</pre>
        </div>
      </body>
    </html>
  `);
});

// Start the Express server
app.listen(port, () => {
  console.log(`Fallback Node.js server listening on port ${port}`);
  console.log('This server is only a placeholder. The Python app should be used instead.');
}); 