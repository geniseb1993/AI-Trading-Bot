
'''
Mock Hume Voice Service

This is a fallback implementation when the real one can't be imported.
'''

from enum import Enum
import logging

logger = logging.getLogger(__name__)

class VoiceStyle(Enum):
    PROFESSIONAL = "Professional trader voice"
    URGENT = "Urgent alert voice"
    CASUAL = "Casual voice"

class HumeVoiceService:
    '''Mock implementation of the HumeVoiceService'''
    
    def __init__(self, api_key=None, secret_key=None):
        self.api_key = api_key
        self.secret_key = secret_key
        logger.info("Mock Hume Voice Service initialized")
    
    def speak(self, text, voice_style=VoiceStyle.PROFESSIONAL, priority="medium"):
        logger.info(f"Mock speak: '{text[:30]}...' with priority {priority}")
        return True
    
    def test_voice(self):
        logger.info("Mock voice test")
        return True
    
    def __del__(self):
        logger.info("Mock Hume Voice Service cleaned up")
