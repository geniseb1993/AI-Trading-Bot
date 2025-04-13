# AI Trading Bot Notification System

This module adds desktop and voice notifications to the AI Trading Bot, providing real-time alerts for important trading events.

## Features

- **Desktop Notifications**: Receive toast notifications for important trading alerts directly on your desktop
- **Voice Notifications**: Get voice alerts for critical trading signals using Hume AI's natural-sounding voices
- **Customizable Settings**: Configure notification priorities, voice settings, and more
- **Multiple Notification Channels**: Support for desktop, voice, email, and SMS notifications

## Setup Instructions

### 1. Install Required Dependencies

Run the setup script to install all required dependencies:

```bash
python setup_notifications.py
```

This script will:
- Install all required Python packages
- Configure the notification settings in config.json
- Offer to test the Hume AI voice service

### 2. Configure Notification Settings

You can configure notification settings in the frontend UI under Settings > Notifications, or by manually editing the `config.json` file:

```json
{
  "notification_settings": {
    "desktop": {
      "enabled": true
    },
    "voice": {
      "enabled": true,
      "use_hume_ai": true,
      "hume_api_key": "your_api_key_here",
      "hume_secret_key": "your_secret_key_here"
    }
  }
}
```

### 3. Testing the Notification System

#### Test Desktop Notifications

Open the `notification-test.html` file in your browser to test desktop notifications:

```bash
# Open the file in your default browser
start notification-test.html  # Windows
open notification-test.html   # Mac
```

#### Test Voice Notifications

Use the test script to try different voice styles:

```bash
# Test professional voice (default)
python test_hume_voice.py

# Test urgent voice style
python test_hume_voice.py --style urgent

# Test casual voice style
python test_hume_voice.py --style casual

# Custom message
python test_hume_voice.py --message "Bitcoin just crossed $50,000 with strong bullish momentum"
```

## Hume AI Voice Integration

This system uses Hume AI's advanced voice technology to provide natural-sounding voice alerts. The voice characteristics are automatically adjusted based on the alert priority:

- **High Priority**: Uses the "Urgent" voice style for critical alerts
- **Medium Priority**: Uses the "Professional" voice style for standard alerts
- **Low Priority**: Uses the "Casual" voice style for informational alerts

## API Endpoints

The notification system exposes several API endpoints that can be used to send notifications:

### Send Voice Notification

```
POST /api/notifications/speak
{
  "message": "The text to speak",
  "priority": "high|medium|low",
  "use_hume": true|false
}
```

### Send Desktop Notification

```
POST /api/notifications/desktop
{
  "title": "Notification title",
  "message": "The notification message",
  "priority": "high|medium|low"
}
```

### Send Any Notification

```
POST /api/notifications
{
  "title": "Notification title",
  "message": "The notification message",
  "notification_type": "email|sms|desktop|voice",
  "priority": "high|medium|low",
  "group": "trade|system|alert|error"
}
```

## Troubleshooting

### No Sound from Voice Notifications

1. Make sure you have speakers or headphones connected and unmuted
2. Check that the voice is enabled in notification settings
3. Verify pygame is properly installed (`pip install pygame`)
4. For Hume AI voices, ensure your internet connection is working

### Desktop Notifications Not Appearing

1. Check browser/system permissions for notifications
2. Ensure desktop notifications are enabled in settings
3. Try restarting the application and browser

## Contributing

To contribute to the notification system, please follow the project's coding standards and submit a pull request.

## License

This notification system is part of the AI Trading Bot project and is subject to the same license terms. 