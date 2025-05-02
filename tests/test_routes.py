import unittest
import json
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import from backend, fall back to api if needed
try:
    from backend.app import app
except ImportError:
    try:
        from api.app import app
    except ImportError:
        from app import app

class TestAPIRoutes(unittest.TestCase):
    """Test the API routes"""
    
    def setUp(self):
        """Set up a test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_endpoint(self):
        """Test the health endpoint"""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get('status'), 'healthy')
    
    def test_test_endpoint(self):
        """Test the test endpoint"""
        response = self.app.get('/api/test')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get('success'), True)
    
if __name__ == '__main__':
    unittest.main() 