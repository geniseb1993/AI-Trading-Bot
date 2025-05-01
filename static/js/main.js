
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
