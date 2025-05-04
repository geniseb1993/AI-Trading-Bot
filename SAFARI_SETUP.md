# Safari Configuration for AI Trading Bot

If you're experiencing connection issues when accessing the AI Trading Bot in Safari on your Mac, please try the following settings changes:

## Enable Cross-Origin Resource Sharing in Safari

1. Open Safari on your Mac
2. Go to Safari menu > Settings (or Preferences)  
3. Click on the **Advanced** tab
4. Check the box that says **Show Develop menu in menu bar**
5. Close the Settings window
6. Now, click on the **Develop** menu in the menu bar
7. Make sure **Disable Cross-Origin Restrictions** is checked
8. Also check **Disable Local File Restrictions**
9. Restart Safari

## Clear Safari Cache and Cookies

1. In Safari, go to Safari menu > Clear History...
2. Select "all history" from the dropdown
3. Click "Clear History"

## Try Using localhost Instead of 127.0.0.1

When accessing the application, use:
- `http://localhost:5001` instead of `http://127.0.0.1:5001`
- `http://localhost:3001` for the frontend interface

## If Still Having Issues:

1. Try using Chrome or Firefox on your Mac, which often have more lenient CORS policies
2. Ensure your Mac firewall is not blocking the application
3. Check that all required ports (5001, 5002, 5003, 3001) are open and not being used by other applications

## Starting the Application on Mac

Run this command in Terminal to start the application with Mac-specific settings:

```bash
# Make the script executable first (one-time setup)
chmod +x start_mac.sh

# Start the application
./start_mac.sh
```

This script includes special configurations for Mac and Safari compatibility. 