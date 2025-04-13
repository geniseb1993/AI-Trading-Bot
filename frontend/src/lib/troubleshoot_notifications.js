/**
 * Notification System Troubleshooter
 * 
 * This script helps diagnose notification issues by checking:
 * 1. Browser support for notifications
 * 2. Permission status
 * 3. Browser voice synthesis support
 * 4. API connectivity
 * 
 * To use, import this module or access via window.troubleshooter
 */

// Check browser notification support and permissions
export function checkNotificationSupport() {
  console.log('\n--- Desktop Notification Support ---');
  
  if (!('Notification' in window)) {
    console.error('❌ Browser does not support desktop notifications');
    return false;
  }
  
  console.log('✅ Browser supports desktop notifications');
  console.log(`Current permission: ${Notification.permission}`);
  
  if (Notification.permission === 'granted') {
    console.log('✅ Permission granted - Desktop notifications should work');
    return true;
  } else if (Notification.permission === 'denied') {
    console.error('❌ Permission denied - User must enable notifications in browser settings');
    console.log('To fix: Check the lock/info icon in your address bar and enable notifications');
    return false;
  } else {
    console.warn('⚠️ Permission not determined - Notifications require user consent');
    console.log('To fix: Use requestPermission() or test notification button to prompt for permission');
    return 'prompt';
  }
}

// Check speech synthesis support
export function checkSpeechSupport() {
  console.log('\n--- Voice Notification Support ---');
  
  if (!('speechSynthesis' in window)) {
    console.error('❌ Browser does not support speech synthesis');
    return false;
  }
  
  console.log('✅ Browser supports speech synthesis');
  
  const voices = window.speechSynthesis.getVoices();
  console.log(`Available voices: ${voices.length}`);
  
  return true;
}

// Check API connection
export async function checkAPIConnection() {
  console.log('\n--- API Connection ---');
  
  try {
    const response = await fetch('/api/test', { method: 'GET' });
    
    if (response.ok) {
      console.log('✅ API connection successful');
      return true;
    } else {
      console.error(`❌ API returned an error: ${response.status} ${response.statusText}`);
      return false;
    }
  } catch (error) {
    console.error('❌ API connection failed:', error.message);
    console.log('To fix: Ensure the Flask API server is running');
    return false;
  }
}

// Test desktop notification
export function testDesktopNotification() {
  if (!('Notification' in window)) {
    console.error('Cannot test: Browser does not support notifications');
    return;
  }
  
  if (Notification.permission === 'granted') {
    const notification = new Notification('Test Notification', {
      body: 'This is a test desktop notification',
      icon: '/logo192.png'
    });
    
    notification.onclick = () => {
      console.log('Notification clicked');
      notification.close();
    };
    
    console.log('✅ Test notification sent');
  } else if (Notification.permission !== 'denied') {
    console.log('Requesting permission...');
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        testDesktopNotification();
      } else {
        console.error('Permission denied by user');
      }
    });
  } else {
    console.error('Cannot test: Notification permission denied');
  }
}

// Test browser speech synthesis
const testSpeechSynthesis = () => {
  console.log('Testing browser speech synthesis...');
  
  if (!window.speechSynthesis) {
    console.error('❌ SpeechSynthesis API not available in this browser');
    return false;
  }
  
  try {
    const utterance = new SpeechSynthesisUtterance('This is a test voice notification from Velma');
    window.speechSynthesis.speak(utterance);
    console.log('✅ SpeechSynthesis API working - you should hear a voice');
    return true;
  } catch (err) {
    console.error(`❌ Error using SpeechSynthesis API: ${err.message}`);
    return false;
  }
};

// Test voice notification
export function testVoiceNotification() {
  if (!('speechSynthesis' in window)) {
    console.error('Cannot test: Browser does not support speech synthesis');
    return;
  }
  
  const utterance = new SpeechSynthesisUtterance('This is a test voice notification from the AI trading bot');
  
  utterance.onstart = () => console.log('Speech started');
  utterance.onend = () => console.log('Speech ended');
  utterance.onerror = (event) => console.error('Speech error:', event.error);
  
  window.speechSynthesis.speak(utterance);
  console.log('✅ Test voice notification sent');
}

// Check settings in NotificationContext
export function checkNotificationSettings() {
  console.log('\n--- Notification Settings ---');
  
  try {
    // Try to access the notification context directly (only works when explicitly exposed)
    const notificationContext = window.__NOTIFICATION_CONTEXT__;
    
    if (!notificationContext) {
      console.warn('⚠️ Could not access notification context directly');
      
      // Try finding React context in dev tools
      console.log('Checking for React DevTools...');
      if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
        console.log('React DevTools detected. Use React DevTools to inspect NotificationContext');
      } else {
        console.log('React DevTools not found. Install React DevTools for better debugging');
      }
      
      return null;
    }
    
    const settings = notificationContext.notificationSettings;
    console.log('Settings:', settings);
    
    if (settings) {
      console.log(`Desktop notifications: ${settings.desktop ? 'Enabled ✅' : 'Disabled ❌'}`);
      console.log(`Voice notifications: ${settings.voice ? 'Enabled ✅' : 'Disabled ❌'}`);
      
      if (settings.voice) {
        console.log(`Voice settings: ${JSON.stringify(settings.voice)}`);
      }
      
      return settings;
    }
    
    return null;
  } catch (error) {
    console.error('Error checking notification settings:', error);
    return null;
  }
}

// Run all checks
export async function runTests() {
  console.log('======== NOTIFICATION TROUBLESHOOTER =========');
  
  const notificationSupport = checkNotificationSupport();
  const speechSupport = checkSpeechSupport();
  const apiConnected = await checkAPIConnection();
  const settings = checkNotificationSettings();
  
  console.log('\n--- Summary ---');
  console.log(`Desktop notifications: ${notificationSupport === true ? 'Available ✅' : notificationSupport === 'prompt' ? 'Needs permission ⚠️' : 'Unavailable ❌'}`);
  console.log(`Voice synthesis: ${speechSupport ? 'Available ✅' : 'Unavailable ❌'}`);
  console.log(`API connection: ${apiConnected ? 'Connected ✅' : 'Disconnected ❌'}`);
  
  console.log('\n--- Recommendations ---');
  
  if (notificationSupport !== true) {
    console.log('- Enable desktop notifications in your browser settings');
  }
  
  if (!apiConnected) {
    console.log('- Start the Flask API server for full notification functionality');
    console.log('- Run `cd api && python app.py` in the terminal');
  }
  
  if (settings && !settings.desktop && !settings.voice) {
    console.log('- Enable notifications in the app settings (click the gear icon in notification panel)');
  }
  
  return {
    browserSupport: !!('Notification' in window),
    notificationPermission: Notification.permission,
    speechSupport: !!('speechSynthesis' in window),
    apiConnected,
    settings
  };
}

// Helper to request permission explicitly
export function requestPermission() {
  if (!('Notification' in window)) {
    console.error('Browser does not support notifications');
    return Promise.reject('Notifications not supported');
  }
  
  console.log('Requesting notification permission...');
  return Notification.requestPermission().then(permission => {
    console.log(`Permission result: ${permission}`);
    return permission;
  });
}

// Create troubleshooter object
const troubleshooter = {
  checkAll: runTests,
  checkNotificationSupport,
  checkSpeechSupport,
  checkAPIConnection,
  checkNotificationSettings,
  testDesktopNotification,
  testVoiceNotification,
  requestPermission
};

// Export troubleshooter to global scope for easy access from console
if (typeof window !== 'undefined') {
  window.troubleshooter = troubleshooter;
}

export default troubleshooter; 