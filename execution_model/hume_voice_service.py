"""
Hume AI Voice Service Module

This module provides text-to-speech capabilities using Hume AI's API
for high-quality voice synthesis for trading notifications.
"""

import os
import base64
import tempfile
import logging
import traceback
from pathlib import Path
import pygame
from hume import HumeClient
from hume.tts import FormatMp3, PostedUtterance
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class VoiceStyle(Enum):
    PROFESSIONAL = "Professional trader voice with a clear, confident tone that sounds authoritative and calm, with a human-like quality and natural intonation."
    URGENT = "Urgent alert voice that conveys importance while remaining professional and clear. The voice should sound human with natural rhythm and emphasis."
    CASUAL = "Casual yet professional voice with a friendly tone for regular updates. The voice should sound naturally human with appropriate warmth."

class HumeVoiceService:
    """Service for generating and playing voice alerts using Hume AI's voice synthesis API"""
    
    def __init__(self, api_key=None, secret_key=None):
        """
        Initialize the Hume voice service
        
        Args:
            api_key: Hume AI API key (defaults to environment variable)
            secret_key: Hume AI Secret key (defaults to environment variable)
        """
        # Get API keys with explicit precedence order for clarity
        self.api_key = None
        if api_key:
            self.api_key = api_key
        elif os.environ.get("HUME_API_KEY"):
            self.api_key = os.environ.get("HUME_API_KEY")
        
        self.secret_key = None
        if secret_key:
            self.secret_key = secret_key
        elif os.environ.get("HUME_SECRET_KEY"):
            self.secret_key = os.environ.get("HUME_SECRET_KEY")
            
        if not self.api_key:
            logger.error("No Hume API key provided. Voice service will not function.")
            return
            
        logger.info(f"Initializing Hume Voice Service with API key: {self.api_key[:5]}...")
        
        try:
            # Initialize Hume client with explicit API key
            self.client = HumeClient(api_key=self.api_key)
            logger.info("Hume client initialized successfully")
            
            # Test connection to Hume API
            logger.info("Testing connection to Hume API...")
            self._test_hume_connection()
        except Exception as e:
            logger.error(f"Failed to initialize Hume client: {str(e)}")
            logger.error(traceback.format_exc())
        
        # Create temp directory for audio files
        self.temp_dir = Path(tempfile.gettempdir()) / "ai_trading_bot_voice"
        self.temp_dir.mkdir(exist_ok=True)
        logger.info(f"Voice temp directory created at: {self.temp_dir}")
        
        # Initialize pygame for audio playback
        try:
            pygame.mixer.init()
            logger.info("Pygame mixer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pygame mixer: {str(e)}")
            
    def _test_hume_connection(self):
        """Test the connection to the Hume AI API"""
        try:
            # Make a small request to verify connectivity
            result = self.client.tts.synthesize_json(
                utterances=[
                    PostedUtterance(
                        text="Test connection",
                        description="Test voice",
                    )
                ],
                format=FormatMp3(),
                num_generations=1,
            )
            if result and hasattr(result, 'generations') and result.generations:
                logger.info("Successfully connected to Hume AI API")
                return True
            else:
                logger.error("Received empty response from Hume AI API")
                return False
        except Exception as e:
            logger.error(f"Error testing Hume AI connection: {str(e)}")
            logger.error(traceback.format_exc())
            return False
        
    def speak(self, text, voice_style=VoiceStyle.PROFESSIONAL, priority="medium"):
        """
        Generate speech from text and play it
        
        Args:
            text: The text to speak
            voice_style: Style of voice to use
            priority: Priority level affecting voice characteristics
            
        Returns:
            bool: Success status
        """
        if not self.api_key or not hasattr(self, 'client'):
            logger.error("Hume Voice Service is not properly initialized")
            return False
            
        try:
            # Adjust voice description based on priority
            voice_description = voice_style.value
            if priority == "high":
                voice_description = VoiceStyle.URGENT.value
            
            logger.info(f"Generating speech for: '{text[:30]}...' with priority: {priority}")
            logger.info(f"Using voice description: {voice_description[:50]}...")
            
            # Prepare the utterance with instructions for more human-like delivery
            full_description = f"{voice_description} Speak with natural pauses and conversational tone that sounds realistic and human."
            
            # Generate the audio using Hume AI
            logger.debug("Calling Hume API for speech synthesis...")
            result = self.client.tts.synthesize_json(
                utterances=[
                    PostedUtterance(
                        text=text,
                        description=full_description,
                    )
                ],
                format=FormatMp3(),
                num_generations=1,
            )
            
            logger.debug(f"Response type: {type(result)}")
            logger.debug(f"Response attributes: {dir(result)}")
            
            # Check if the result has generations
            if not hasattr(result, 'generations') or not result.generations:
                logger.error("No generations found in Hume API response")
                return False
                
            # Extract the first generation
            generation = result.generations[0]
            logger.debug(f"Generation data: {generation}")
            
            # Extract the base64-encoded audio
            audio_base64 = generation.audio
            if not audio_base64:
                logger.error("No audio data received from Hume API")
                return False
                
            logger.debug(f"Received audio data of length: {len(audio_base64)}")
            
            # Save to temporary file
            temp_file = self.temp_dir / f"notification_{hash(text)}.mp3"
            with open(temp_file, "wb") as f:
                f.write(base64.b64decode(audio_base64))
            
            logger.info(f"Audio file saved to: {temp_file}")
            
            # Play the audio
            self._play_audio(temp_file)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in speech synthesis: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def _play_audio(self, file_path):
        """
        Play audio file using pygame
        
        Args:
            file_path: Path to the audio file
        """
        try:
            logger.info(f"Playing audio from: {file_path}")
            pygame.mixer.music.load(str(file_path))
            pygame.mixer.music.play()
            logger.debug("Audio playback started")
            
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            logger.debug("Audio playback completed")
                
        except Exception as e:
            logger.error(f"Error playing audio: {str(e)}")
            logger.error(traceback.format_exc())
            
    def test_voice(self):
        """Test the voice service with a sample notification"""
        logger.info("Running voice service test")
        return self.speak(
            "This is a test notification from the AI Trading Bot. A trading opportunity has been detected for Apple stock at a price of 195 dollars and 67 cents. If you're hearing this in a natural human-like voice, the Hume AI integration is working correctly."
        )
        
    def __del__(self):
        """Cleanup when the object is destroyed"""
        try:
            pygame.mixer.quit()
            logger.info("Pygame mixer cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up pygame mixer: {str(e)}")
            pass 