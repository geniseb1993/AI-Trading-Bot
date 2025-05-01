#!/bin/bash
# Create required directories and static files for the frontend
set -e

echo "Setting up static files for Vicki Trading Bot..."

# Create required directories
mkdir -p frontend/build/static/css
mkdir -p frontend/build/static/js
mkdir -p frontend/build/images

# Check if index.html exists, create if not
if [ ! -f frontend/build/index.html ]; then
    echo "Creating index.html..."
    cat > frontend/build/index.html << 'EOL'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vicki AI Trading Bot</title>
    <link rel="stylesheet" href="/static/css/main.8a689c36.css">
</head>
<body>
    <div id="root"></div>
    <script src="/static/js/main.75e22b8e.js"></script>
</body>
</html>
EOL
fi

# Create CSS file
echo "Creating CSS file..."
cat > frontend/build/static/css/main.8a689c36.css << 'EOL'
/* Static CSS file created by setup script */
body {
    font-family: Arial, sans-serif;
    background-color: #121212;
    color: #ffffff;
    margin: 0;
    padding: 0;
}
#root {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.app-container {
    max-width: 1200px;
    width: 100%;
    padding: 20px;
    box-sizing: border-box;
}
.placeholder-message {
    text-align: center;
    margin-top: 100px;
    font-size: 1.5rem;
}
h1 {
    color: #61dafb;
}
EOL

# Create JS file
echo "Creating JS file..."
cat > frontend/build/static/js/main.75e22b8e.js << 'EOL'
// Static JS file created by setup script
console.log('Emergency JS file loaded by setup script');
document.addEventListener('DOMContentLoaded', function() {
    const root = document.getElementById('root');
    if (root) {
        root.innerHTML = `
            <div class="app-container">
                <div class="placeholder-message">
                    <h1>Vicki AI Trading Bot</h1>
                    <p>This is an emergency interface created by the setup script.</p>
                    <p>The frontend build files were not properly created or are inaccessible.</p>
                    <p>Please visit <a href="/api/diagnostic" style="color: #61dafb;">Diagnostic Information</a> to debug the issue.</p>
                    <div style="margin-top: 40px; text-align: left;">
                        <h2>API Endpoints:</h2>
                        <ul>
                            <li><a href="/api/health" style="color: #61dafb;">Health Check</a></li>
                            <li><a href="/api/bot/status" style="color: #61dafb;">Bot Status</a></li>
                            <li><a href="/api/market-overview" style="color: #61dafb;">Market Overview</a></li>
                            <li><a href="/api/portfolio-performance" style="color: #61dafb;">Portfolio Performance</a></li>
                            <li><a href="/api/diagnostic" style="color: #61dafb;">Diagnostic Information</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }
});
EOL

# Create manifest.json if it doesn't exist
if [ ! -f frontend/build/manifest.json ]; then
    echo "Creating manifest.json..."
    cat > frontend/build/manifest.json << 'EOL'
{
  "short_name": "Vicki",
  "name": "Vicki AI Trading Bot",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    },
    {
      "src": "images/vicky.png",
      "type": "image/png",
      "sizes": "192x192"
    },
    {
      "src": "images/vicky.png",
      "type": "image/png",
      "sizes": "512x512"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}
EOL
fi

# Set permissions
echo "Setting permissions..."
chmod -R 755 frontend/build

# Run python fix script if it exists
if [ -f fix_frontend_build.py ]; then
    echo "Running fix_frontend_build.py..."
    python fix_frontend_build.py
fi

echo "Static file setup complete." 