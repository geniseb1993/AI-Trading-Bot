/**
 * API Proxy Configuration
 * 
 * This file defines which API routes should be redirected to the simplified bot management server
 * rather than the main API server to prevent timeout issues.
 */

const botManagementRoutes = [
  '/api/bot/status',
  '/api/bot/start',
  '/api/bot/stop',
  '/api/status',
  '/api/dual-bot/status',
  '/api/ai-activity/logs',
  '/api/ai-activity/activity-types'
];

// The URL of the simplified bot management server
const botManagementServerUrl = 'http://localhost:5002';

// The URL of the main API server
const mainApiServerUrl = 'http://localhost:5001';

/**
 * Determines which server a request should be routed to
 * @param {string} path - The API path
 * @returns {string} The appropriate server URL
 */
function getProxyTarget(path) {
  // Check if the path starts with any of the bot management routes
  for (const route of botManagementRoutes) {
    if (path.startsWith(route)) {
      console.log(`Routing ${path} to bot management server`);
      return botManagementServerUrl;
    }
  }
  
  // Default to the main API server
  return mainApiServerUrl;
}

module.exports = {
  botManagementRoutes,
  botManagementServerUrl,
  mainApiServerUrl,
  getProxyTarget
}; 