"""
Mock implementation of the plyer module.
This provides a minimal implementation of the notification functionality.
"""

class _NotificationMock:
    """Mock implementation of plyer notification module"""
    
    def __init__(self):
        self.title = None
        self.message = None
        self.app_name = None
        self.timeout = 10
    
    def notify(self, title='', message='', app_name='', app_icon='', timeout=10, ticker=''):
        """Mock implementation of notify method"""
        import logging
        
        self.title = title
        self.message = message
        self.app_name = app_name or 'AI Trading Bot'
        self.timeout = timeout
        
        logging.info(f"NOTIFICATION: {title} - {message}")
        
        return True

# Create singleton instance
notification = _NotificationMock()

# For imports like: from plyer import notification
__all__ = ['notification'] 