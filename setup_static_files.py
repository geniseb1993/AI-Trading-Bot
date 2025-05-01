#!/usr/bin/env python
"""
Setup Static Files

This script creates a simplified structure of static files that Flask can easily serve.
It places all required frontend files in standard locations under the /static directory.
"""

import os
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_static_files():
    """Set up static files in a structure that's easy for Flask to serve."""
    # Define directories
    static_dir = Path('static')
    css_dir = static_dir / 'css'
    js_dir = static_dir / 'js'
    images_dir = static_dir / 'images'
    
    # Create directories
    for directory in [static_dir, css_dir, js_dir, images_dir]:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    # Create index.html in the root directory
    with open('index.html', 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vicki AI Trading Bot</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div id="root"></div>
    <script src="/static/js/main.js"></script>
</body>
</html>""")
    logger.info("Created index.html in root directory")
    
    # Create CSS file
    with open(css_dir / 'main.css', 'w') as f:
        f.write("""
/* Main CSS file for Vicki AI Trading Bot */
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
.panel {
    background-color: #1e1e1e;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.button {
    background-color: #61dafb;
    color: #121212;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    transition: background-color 0.3s;
}
.button:hover {
    background-color: #4fa8d1;
}
a {
    color: #61dafb;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}
""")
    logger.info("Created main.css file")
    
    # Create JS file
    with open(js_dir / 'main.js', 'w') as f:
        f.write("""
// Main JavaScript file for Vicki AI Trading Bot
console.log('Vicki AI Trading Bot interface loaded');

// Helper function to create HTML elements
function createElement(tag, attributes = {}, children = []) {
    const element = document.createElement(tag);
    
    // Set attributes
    Object.entries(attributes).forEach(([key, value]) => {
        if (key === 'className') {
            element.className = value;
        } else if (key === 'innerHTML') {
            element.innerHTML = value;
        } else {
            element.setAttribute(key, value);
        }
    });
    
    // Append children
    children.forEach(child => {
        if (typeof child === 'string') {
            element.appendChild(document.createTextNode(child));
        } else {
            element.appendChild(child);
        }
    });
    
    return element;
}

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    const root = document.getElementById('root');
    if (!root) return;
    
    // Create app container
    const appContainer = createElement('div', { className: 'app-container' });
    root.appendChild(appContainer);
    
    // Create header
    const header = createElement('header', { className: 'panel' }, [
        createElement('h1', {}, ['Vicki AI Trading Bot']),
        createElement('p', {}, ['Welcome to your AI-powered trading assistant'])
    ]);
    appContainer.appendChild(header);
    
    // Create navigation
    const nav = createElement('nav', { className: 'panel' }, [
        createElement('h2', {}, ['Navigation']),
        createElement('div', { style: 'display: flex; gap: 10px;' }, [
            createElement('a', { href: '#dashboard', className: 'button' }, ['Dashboard']),
            createElement('a', { href: '#market', className: 'button' }, ['Market Data']),
            createElement('a', { href: '#portfolio', className: 'button' }, ['Portfolio']),
            createElement('a', { href: '#settings', className: 'button' }, ['Settings'])
        ])
    ]);
    appContainer.appendChild(nav);
    
    // Create main content area
    const main = createElement('main', { className: 'panel' }, [
        createElement('h2', {}, ['Dashboard']),
        createElement('div', { id: 'dashboard-content' }, [
            createElement('p', {}, ['Loading dashboard data...'])
        ])
    ]);
    appContainer.appendChild(main);
    
    // Create API links section
    const apiSection = createElement('section', { className: 'panel' }, [
        createElement('h2', {}, ['API Access']),
        createElement('ul', {}, [
            createElement('li', {}, [
                createElement('a', { href: '/api/health', target: '_blank' }, ['Health Check'])
            ]),
            createElement('li', {}, [
                createElement('a', { href: '/api/bot/status', target: '_blank' }, ['Bot Status'])
            ]),
            createElement('li', {}, [
                createElement('a', { href: '/api/market-overview', target: '_blank' }, ['Market Overview'])
            ]),
            createElement('li', {}, [
                createElement('a', { href: '/api/portfolio-performance', target: '_blank' }, ['Portfolio Performance'])
            ]),
            createElement('li', {}, [
                createElement('a', { href: '/api/diagnostic', target: '_blank' }, ['Diagnostic Information'])
            ])
        ])
    ]);
    appContainer.appendChild(apiSection);
    
    // Create footer
    const footer = createElement('footer', { className: 'panel', style: 'margin-top: 20px; text-align: center;' }, [
        createElement('p', {}, ['© 2023 Vicki AI Trading Bot | All rights reserved'])
    ]);
    appContainer.appendChild(footer);
    
    // Simulate loading dashboard data
    setTimeout(() => {
        const dashboardContent = document.getElementById('dashboard-content');
        if (dashboardContent) {
            dashboardContent.innerHTML = `
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div class="panel" style="background-color: #2a2a2a;">
                        <h3>Market Summary</h3>
                        <p>S&P 500: <span style="color: #4caf50;">+1.2%</span></p>
                        <p>NASDAQ: <span style="color: #4caf50;">+0.8%</span></p>
                        <p>DOW: <span style="color: #f44336;">-0.3%</span></p>
                    </div>
                    <div class="panel" style="background-color: #2a2a2a;">
                        <h3>Portfolio Summary</h3>
                        <p>Total Value: $125,430.50</p>
                        <p>Daily Change: <span style="color: #4caf50;">+$1,230.25 (+0.98%)</span></p>
                        <p>Open Positions: 12</p>
                    </div>
                </div>
                <div class="panel" style="background-color: #2a2a2a; margin-top: 20px;">
                    <h3>Recent Signals</h3>
                    <ul>
                        <li>AAPL: <span style="color: #4caf50;">BUY</span> - Strong momentum detected</li>
                        <li>MSFT: <span style="color: #4caf50;">BUY</span> - Breakout from resistance</li>
                        <li>TSLA: <span style="color: #f44336;">SELL</span> - Bearish divergence</li>
                        <li>AMZN: <span style="color: #ff9800;">HOLD</span> - Consolidating at support</li>
                    </ul>
                </div>
            `;
        }
    }, 1000);
});
""")
    logger.info("Created main.js file")
    
    # Create a sample image in the images directory
    try:
        # Try to copy an existing image if available
        found_image = False
        for src_path in [
            Path('frontend/public/images/vicky.png'),
            Path('frontend/public/images/velma.png'),
            Path('public/images/vicky.png')
        ]:
            if src_path.exists():
                shutil.copy(src_path, images_dir / 'logo.png')
                logger.info(f"Copied {src_path} to {images_dir / 'logo.png'}")
                found_image = True
                break
        
        if not found_image:
            # Create a simple text file explaining the image is missing
            with open(images_dir / 'logo.txt', 'w') as f:
                f.write("Logo image not found. Please add an image here.")
            logger.info("Created placeholder logo.txt file")
    except Exception as e:
        logger.error(f"Error copying logo image: {e}")
    
    # Create a manifest.json file
    with open(static_dir / 'manifest.json', 'w') as f:
        f.write("""{
  "short_name": "Vicki",
  "name": "Vicki AI Trading Bot",
  "icons": [
    {
      "src": "/static/images/logo.png",
      "type": "image/png",
      "sizes": "192x192"
    }
  ],
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#121212"
}""")
    logger.info("Created manifest.json file")
    
    # Create a robots.txt file
    with open(static_dir / 'robots.txt', 'w') as f:
        f.write("""User-agent: *
Allow: /""")
    logger.info("Created robots.txt file")
    
    # Copy any existing CSS and JS files from the frontend build
    try:
        frontend_css = Path('frontend/build/static/css')
        if frontend_css.exists():
            for css_file in frontend_css.glob('*.css'):
                shutil.copy(css_file, css_dir)
                logger.info(f"Copied {css_file} to {css_dir}")
        
        frontend_js = Path('frontend/build/static/js')
        if frontend_js.exists():
            for js_file in frontend_js.glob('*.js'):
                shutil.copy(js_file, js_dir)
                logger.info(f"Copied {js_file} to {js_dir}")
    except Exception as e:
        logger.error(f"Error copying frontend files: {e}")
    
    logger.info("Static file setup complete")
    return True

if __name__ == "__main__":
    setup_static_files() 