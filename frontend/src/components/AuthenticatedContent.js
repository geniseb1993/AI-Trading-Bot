import React, { useContext } from 'react';
import NotificationContext from '../contexts/NotificationContext';
import NotificationBell from './NotificationBell';

const AuthenticatedContent = ({ children }) => {
  try {
    const notificationContext = useContext(NotificationContext);
    if (!notificationContext) {
      console.warn('NotificationContext not available in AuthenticatedContent');
      return null;
    }
    return children;
  } catch (error) {
    console.error('Error accessing NotificationContext:', error);
    return null;
  }
};

export const AuthenticatedNotificationBell = () => {
  return (
    <AuthenticatedContent>
      <NotificationBell />
    </AuthenticatedContent>
  );
};

export default AuthenticatedContent; 