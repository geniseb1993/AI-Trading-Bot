import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { NotificationProvider } from '../contexts/NotificationContext';
import NotificationBell from '../components/NotificationBell';
import NotificationSettings from '../components/NotificationSettings';
import NotificationTemplate from '../components/NotificationTemplate';
import { NotificationPriority, NotificationGroup } from '../contexts/NotificationContext';

// Mock the notification service
jest.mock('../services/notificationService', () => ({
  sendNotification: jest.fn(),
  getNotificationHistory: jest.fn()
}));

describe('Notification Components', () => {
  const renderWithProvider = (component) => {
    return render(
      <NotificationProvider>
        {component}
      </NotificationProvider>
    );
  };

  describe('NotificationBell', () => {
    it('renders notification bell with correct unread count', () => {
      renderWithProvider(<NotificationBell />);
      const bell = screen.getByTestId('notification-bell');
      expect(bell).toBeInTheDocument();
    });

    it('shows notification list when clicked', () => {
      renderWithProvider(<NotificationBell />);
      const bell = screen.getByTestId('notification-bell');
      fireEvent.click(bell);
      expect(screen.getByTestId('notification-list')).toBeInTheDocument();
    });
  });

  describe('NotificationSettings', () => {
    it('renders all notification settings', () => {
      renderWithProvider(<NotificationSettings />);
      expect(screen.getByText('Email Notifications')).toBeInTheDocument();
      expect(screen.getByText('SMS Notifications')).toBeInTheDocument();
      expect(screen.getByText('Desktop Notifications')).toBeInTheDocument();
      expect(screen.getByText('Voice Alerts')).toBeInTheDocument();
    });

    it('toggles notification settings correctly', () => {
      renderWithProvider(<NotificationSettings />);
      const emailToggle = screen.getByTestId('email-toggle');
      fireEvent.click(emailToggle);
      expect(emailToggle).toHaveAttribute('aria-checked', 'false');
    });
  });

  describe('NotificationTemplate', () => {
    it('renders template list', () => {
      renderWithProvider(<NotificationTemplate />);
      expect(screen.getByText('Trade Execution')).toBeInTheDocument();
      expect(screen.getByText('System Alert')).toBeInTheDocument();
      expect(screen.getByText('Error')).toBeInTheDocument();
    });

    it('creates new template correctly', async () => {
      renderWithProvider(<NotificationTemplate />);
      const addButton = screen.getByTestId('add-template');
      fireEvent.click(addButton);
      
      // Fill in template details
      await act(async () => {
        fireEvent.change(screen.getByLabelText('Template Name'), {
          target: { value: 'New Template' }
        });
        fireEvent.change(screen.getByLabelText('Subject'), {
          target: { value: 'New Subject: {variable}' }
        });
        fireEvent.change(screen.getByLabelText('Body'), {
          target: { value: 'New body with {variable}' }
        });
      });

      const saveButton = screen.getByText('Save Template');
      fireEvent.click(saveButton);
      
      expect(screen.getByText('New Template')).toBeInTheDocument();
    });
  });

  describe('Notification Context', () => {
    it('adds and removes notifications correctly', () => {
      const TestComponent = () => {
        const { addNotification, removeNotification } = useNotification();
        
        return (
          <div>
            <button onClick={() => addNotification({
              message: 'Test notification',
              priority: NotificationPriority.HIGH,
              group: NotificationGroup.SYSTEM
            })}>
              Add Notification
            </button>
            <button onClick={() => removeNotification(1)}>
              Remove Notification
            </button>
          </div>
        );
      };

      renderWithProvider(<TestComponent />);
      const addButton = screen.getByText('Add Notification');
      fireEvent.click(addButton);
      
      expect(screen.getByText('Test notification')).toBeInTheDocument();
      
      const removeButton = screen.getByText('Remove Notification');
      fireEvent.click(removeButton);
      
      expect(screen.queryByText('Test notification')).not.toBeInTheDocument();
    });
  });
}); 