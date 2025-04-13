import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tooltip
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  ContentCopy as CopyIcon
} from '@mui/icons-material';
import { useNotification, NotificationPriority, NotificationGroup } from '../contexts/NotificationContext';

const NotificationTemplate = () => {
  const [templates, setTemplates] = useState([
    {
      id: 1,
      name: 'Trade Execution',
      subject: 'Trade Executed: {symbol}',
      body: 'A {action} order for {symbol} has been executed at {price}',
      group: NotificationGroup.TRADE,
      priority: NotificationPriority.HIGH
    },
    {
      id: 2,
      name: 'System Alert',
      subject: 'System Alert: {title}',
      body: '{message}',
      group: NotificationGroup.SYSTEM,
      priority: NotificationPriority.MEDIUM
    },
    {
      id: 3,
      name: 'Error',
      subject: 'Error: {title}',
      body: '{message}',
      group: NotificationGroup.ERROR,
      priority: NotificationPriority.HIGH
    }
  ]);

  const [openDialog, setOpenDialog] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    subject: '',
    body: '',
    group: NotificationGroup.SYSTEM,
    priority: NotificationPriority.MEDIUM
  });

  const handleOpenDialog = (template = null) => {
    if (template) {
      setEditingTemplate(template);
      setFormData(template);
    } else {
      setEditingTemplate(null);
      setFormData({
        name: '',
        subject: '',
        body: '',
        group: NotificationGroup.SYSTEM,
        priority: NotificationPriority.MEDIUM
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingTemplate(null);
  };

  const handleInputChange = (field) => (event) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleSaveTemplate = () => {
    if (editingTemplate) {
      setTemplates(prev =>
        prev.map(template =>
          template.id === editingTemplate.id
            ? { ...formData, id: template.id }
            : template
        )
      );
    } else {
      setTemplates(prev => [
        ...prev,
        { ...formData, id: Date.now() }
      ]);
    }
    handleCloseDialog();
  };

  const handleDeleteTemplate = (templateId) => {
    setTemplates(prev => prev.filter(template => template.id !== templateId));
  };

  const handleDuplicateTemplate = (template) => {
    setTemplates(prev => [
      ...prev,
      {
        ...template,
        id: Date.now(),
        name: `${template.name} (Copy)`
      }
    ]);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Notification Templates
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          New Template
        </Button>
      </Box>

      <Paper>
        <List>
          {templates.map((template) => (
            <ListItem
              key={template.id}
              divider
              sx={{
                '&:hover': {
                  bgcolor: 'action.hover'
                }
              }}
            >
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle1">
                      {template.name}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{
                        bgcolor: 'primary.main',
                        color: 'primary.contrastText',
                        px: 1,
                        py: 0.5,
                        borderRadius: 1
                      }}
                    >
                      {template.group}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{
                        bgcolor: 'error.main',
                        color: 'error.contrastText',
                        px: 1,
                        py: 0.5,
                        borderRadius: 1
                      }}
                    >
                      {template.priority}
                    </Typography>
                  </Box>
                }
                secondary={
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" color="textSecondary">
                      Subject: {template.subject}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Body: {template.body}
                    </Typography>
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                <Tooltip title="Edit">
                  <IconButton
                    edge="end"
                    onClick={() => handleOpenDialog(template)}
                    sx={{ mr: 1 }}
                  >
                    <EditIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Duplicate">
                  <IconButton
                    edge="end"
                    onClick={() => handleDuplicateTemplate(template)}
                    sx={{ mr: 1 }}
                  >
                    <CopyIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Delete">
                  <IconButton
                    edge="end"
                    onClick={() => handleDeleteTemplate(template.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Paper>

      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingTemplate ? 'Edit Template' : 'New Template'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Template Name"
                value={formData.name}
                onChange={handleInputChange('name')}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Subject Template"
                value={formData.subject}
                onChange={handleInputChange('subject')}
                helperText="Use {variable} for dynamic content"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Body Template"
                value={formData.body}
                onChange={handleInputChange('body')}
                helperText="Use {variable} for dynamic content"
              />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Group</InputLabel>
                <Select
                  value={formData.group}
                  onChange={handleInputChange('group')}
                  label="Group"
                >
                  {Object.values(NotificationGroup).map((group) => (
                    <MenuItem key={group} value={group}>
                      {group.charAt(0).toUpperCase() + group.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={formData.priority}
                  onChange={handleInputChange('priority')}
                  label="Priority"
                >
                  {Object.values(NotificationPriority).map((priority) => (
                    <MenuItem key={priority} value={priority}>
                      {priority.charAt(0).toUpperCase() + priority.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSaveTemplate}
            disabled={!formData.name || !formData.subject || !formData.body}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default NotificationTemplate; 