import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormGroup,
  FormControlLabel,
  Switch,
  Typography,
  Box,
  Divider,
  Grid,
  TextField,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  Slider,
  Alert,
  RadioGroup,
  Radio
} from '@mui/material';
import { useNotification, NotificationPriority, NotificationGroup } from '../contexts/NotificationContext';
import axios from 'axios';

// Default notification settings
const defaultSettings = {
  desktop: true,
  voice: false,
  sound: true,
  email: false,
  sms: false,
  priorityLevels: {
    [NotificationPriority.HIGH]: true,
    [NotificationPriority.MEDIUM]: true,
    [NotificationPriority.LOW]: true
  },
  voice: {
    rate: 150,
    volume: 0.8,
    useHumeAI: true
  }
};

const NotificationSettings = ({ open, onClose }) => {
  const { notificationSettings, updateNotificationSettings, sendDesktopNotification, sendVoiceNotification } = useNotification() || {};
  const [permissionStatus, setPermissionStatus] = useState('');
  const [voiceTest, setVoiceTest] = useState(false);
  const [testingDesktop, setTestingDesktop] = useState(false);
  const [testingVoice, setTestingVoice] = useState(false);
  const [status, setStatus] = useState({});
  const [selectedVoiceService, setSelectedVoiceService] = useState('default');
  
  // Use default settings if notificationSettings is undefined
  const settings = notificationSettings || defaultSettings;
  
  // Check for notification permissions on component mount
  useEffect(() => {
    if ("Notification" in window) {
      setPermissionStatus(Notification.permission);
    } else {
      setPermissionStatus('not-supported');
    }
  }, []);
  
  // Handle notification permission request
  const requestNotificationPermission = async () => {
    if ("Notification" in window) {
      const permission = await Notification.requestPermission();
      setPermissionStatus(permission);
    }
  };

  const handleToggle = (setting) => {
    if (updateNotificationSettings) {
      updateNotificationSettings({
      ...settings,
      [setting]: !settings[setting]
    });
    }
  };

  const handlePriorityToggle = (priority) => {
    if (updateNotificationSettings) {
      updateNotificationSettings({
      ...settings,
      priorityLevels: {
        ...settings.priorityLevels,
          [priority]: !settings.priorityLevels?.[priority]
        }
      });
    }
  };
  
  // Handle voice settings change
  const handleVoiceSettingChange = (setting, value) => {
    if (updateNotificationSettings) {
      updateNotificationSettings({
      ...settings,
        voice: {
          ...settings.voice,
          [setting]: value
        }
      });
    }
  };
  
  // Check if the notifications api is available
  const testDesktopNotification = async () => {
    try {
      setTestingDesktop(true);
      
      const response = await axios.post('/api/notifications/desktop', {
        title: "Test Notification",
        message: "This is a test notification from Velma"
      });
      
      if (response.data && response.data.success) {
        setStatus({ ...status, desktop: 'Notification sent successfully! Check your desktop.' });
      }
    } catch (err) {
      console.error('Error testing desktop notification:', err);
      setStatus({ ...status, desktop: `Error: ${err.message}` });
    } finally {
      setTestingDesktop(false);
    }
  };
  
  // Test voice notification function
  const testVoiceNotification = async () => {
    try {
      setTestingVoice(true);
      
      const response = await axios.post('/api/notifications/speak', {
        message: "This is a test notification from Velma",
        priority: "normal",
        voice_service: selectedVoiceService
      });
      
      if (response.data && response.data.success) {
        setStatus({ ...status, voice: 'Voice notification sent! You should hear it now.' });
      }
    } catch (err) {
      console.error('Error testing voice notification:', err);
      setStatus({ ...status, voice: `Error: ${err.message}` });
    } finally {
      setTestingVoice(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Notification Settings</DialogTitle>
      <DialogContent>
        <Grid container spacing={3}>
          {permissionStatus === 'denied' && (
            <Grid item xs={12}>
              <Alert severity="warning">
                Desktop notifications are blocked by your browser. Please update your browser settings to allow notifications.
              </Alert>
            </Grid>
          )}
          
          {permissionStatus === 'not-supported' && (
            <Grid item xs={12}>
              <Alert severity="info">
                Your browser does not support desktop notifications.
              </Alert>
            </Grid>
          )}
          
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Notification Channels
            </Typography>
            <FormGroup>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.email}
                    onChange={() => handleToggle('email')}
                  />
                }
                label="Email Notifications"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.sms}
                    onChange={() => handleToggle('sms')}
                  />
                }
                label="SMS Notifications"
              />
              <Grid container alignItems="center">
                <Grid item>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.desktop}
                    onChange={() => handleToggle('desktop')}
                  />
                }
                label="Desktop Notifications"
              />
                </Grid>
                <Grid item>
                  {permissionStatus === 'default' && (
                    <Button 
                      variant="outlined" 
                      size="small" 
                      onClick={requestNotificationPermission}
                      sx={{ ml: 2 }}
                    >
                      Request Permission
                    </Button>
                  )}
                  {settings.desktop && permissionStatus === 'granted' && (
                    <Button 
                      variant="outlined" 
                      size="small" 
                      onClick={testDesktopNotification}
                      sx={{ ml: 2 }}
                    >
                      Test Notification
                    </Button>
                  )}
                </Grid>
              </Grid>
              <Grid container alignItems="center">
                <Grid item>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.voice}
                    onChange={() => handleToggle('voice')}
                  />
                }
                label="Voice Notifications"
                  />
                </Grid>
                <Grid item>
                  {settings.voice && (
                    <Button 
                      variant="outlined" 
                      size="small" 
                      onClick={testVoiceNotification}
                      disabled={voiceTest}
                      sx={{ ml: 2 }}
                    >
                      {voiceTest ? 'Testing...' : 'Test Voice'}
                    </Button>
                  )}
                </Grid>
              </Grid>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.sound}
                    onChange={() => handleToggle('sound')}
                  />
                }
                label="Sound Alerts"
              />
            </FormGroup>
          </Grid>

          <Grid item xs={12}>
            <Divider />
          </Grid>

          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Priority Levels
            </Typography>
            <Typography variant="body2" gutterBottom>
              Select which priority levels should trigger notifications
            </Typography>
            <FormGroup>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.priorityLevels?.[NotificationPriority.HIGH] || false}
                    onChange={() => handlePriorityToggle(NotificationPriority.HIGH)}
                  />
                }
                label="High Priority"
              />
                <FormControlLabel
                  control={
                    <Switch
                    checked={settings.priorityLevels?.[NotificationPriority.MEDIUM] || false}
                    onChange={() => handlePriorityToggle(NotificationPriority.MEDIUM)}
                  />
                }
                label="Medium Priority"
              />
                <FormControlLabel
                  control={
                    <Switch
                    checked={settings.priorityLevels?.[NotificationPriority.LOW] || false}
                    onChange={() => handlePriorityToggle(NotificationPriority.LOW)}
                    />
                  }
                label="Low Priority"
                />
            </FormGroup>
          </Grid>

          {settings.voice && (
            <>
          <Grid item xs={12}>
            <Divider />
          </Grid>

          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
                  Voice Notification Settings
                </Typography>
                
                <Typography variant="subtitle2" gutterBottom>
                  Voice Engine
            </Typography>
                <RadioGroup
                  row
                  value={settings.voice?.useHumeAI ? 'hume' : 'default'}
                  onChange={(e) => handleVoiceSettingChange('useHumeAI', e.target.value === 'hume')}
                >
                  <FormControlLabel 
                    value="hume" 
                    control={<Radio />} 
                    label="Hume AI (Natural Voice)" 
                  />
              <FormControlLabel
                    value="default" 
                    control={<Radio />} 
                    label="System Default" 
                  />
                </RadioGroup>
                
                <Box sx={{ pl: 2, pr: 2, mt: 2 }}>
                  <Typography id="voice-rate-slider" gutterBottom>
                    Speech Rate
                  </Typography>
                  <Slider
                    aria-labelledby="voice-rate-slider"
                    valueLabelDisplay="auto"
                    step={10}
                    marks
                    min={100}
                    max={200}
                    value={settings.voice?.rate || 150}
                    onChange={(e, newValue) => handleVoiceSettingChange('rate', newValue)}
                    disabled={settings.voice?.useHumeAI}
                  />
                  
                  <Typography id="voice-volume-slider" gutterBottom>
                    Volume
                  </Typography>
                  <Slider
                    aria-labelledby="voice-volume-slider"
                    valueLabelDisplay="auto"
                    step={0.1}
                    marks
                    min={0.1}
                    max={1.0}
                    value={settings.voice?.volume || 0.8}
                    onChange={(e, newValue) => handleVoiceSettingChange('volume', newValue)}
                    disabled={settings.voice?.useHumeAI}
                  />
                  
                  {settings.voice?.useHumeAI && (
                    <Alert severity="info" sx={{ mt: 2 }}>
                      Hume AI uses advanced AI models to generate natural-sounding voices optimized for trading alerts.
                      Speech rate and volume are automatically optimized based on the alert priority.
                    </Alert>
                  )}
                </Box>
          </Grid>
            </>
          )}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          Save & Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default NotificationSettings; 