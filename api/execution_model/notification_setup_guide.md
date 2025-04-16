# Notification System Setup Guide

This guide explains how to configure different notification channels in the trading bot.

## 1. Email Notifications

To set up email notifications:

1. Update the `config.py` file with your email settings:
```python
"notifications": {
    "email_enabled": True,
    "email_sender": "your.email@gmail.com",
    "email_password": "your-app-specific-password",
    "email_recipients": ["recipient1@email.com", "recipient2@email.com"],
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
}
```

For Gmail:
1. Enable 2-factor authentication
2. Generate an App Password:
   - Go to Google Account Settings
   - Security
   - App Passwords
   - Generate a new app password for the trading bot

## 2. SMS Notifications (Twilio)

To set up SMS notifications:

1. Sign up for a Twilio account at https://www.twilio.com
2. Get your Account SID and Auth Token from the Twilio Console
3. Get a Twilio phone number
4. Update the `config.py` file:
```python
"notifications": {
    "sms_enabled": True,
    "twilio_account_sid": "your_account_sid",
    "twilio_auth_token": "your_auth_token",
    "twilio_from_number": "+1234567890",
    "twilio_to_numbers": ["+1987654321"]
}
```

## 3. Desktop Notifications

Desktop notifications are enabled by default. To customize:

```python
"notifications": {
    "desktop_enabled": True
}
```

## 4. Voice Alerts

To set up voice alerts:

1. Install the required text-to-speech engine:
   - Windows: Windows Speech API (built-in)
   - Linux: `espeak` or `festival`
   - macOS: `say` command (built-in)

2. Update the configuration:
```python
"notifications": {
    "voice_enabled": True,
    "voice_command": "say"  # or "espeak" for Linux
}
```

## 5. Notification Preferences

Configure which events trigger notifications:

```python
"notifications": {
    "alert_on_entry": True,
    "alert_on_exit": True,
    "alert_on_stop_loss": True,
    "alert_on_profit_target": True,
    "alert_on_risk_breach": True,
    "alert_on_system_error": True,
    "alert_cooldown_minutes": 5
}
```

## 6. Testing Notifications

Run the test script to verify your notification setup:

```bash
python execution_model/test_notifications.py
```

## Security Notes

1. Never commit sensitive credentials to version control
2. Use environment variables or a secure credential manager
3. Regularly rotate passwords and API keys
4. Monitor notification logs for any security issues

## Troubleshooting

1. Email Notifications:
   - Check SMTP server settings
   - Verify email credentials
   - Check spam folder

2. SMS Notifications:
   - Verify Twilio credentials
   - Check phone number format
   - Monitor Twilio console for errors

3. Desktop Notifications:
   - Check system notification settings
   - Verify Python has notification permissions

4. Voice Alerts:
   - Verify text-to-speech engine installation
   - Check system audio settings
   - Test voice command manually 