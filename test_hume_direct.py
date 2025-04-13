"""
Direct test for Hume AI API without going through the framework.
This simple script makes a direct API call to Hume AI to verify it's working.
"""

from hume import HumeClient
from hume.tts import FormatMp3, PostedUtterance
import base64
import tempfile
from pathlib import Path
import pygame
import time
import logging

# Enable logging to see detailed error messages
logging.basicConfig(level=logging.DEBUG)

# Initialize pygame for audio playback
pygame.mixer.init()

# API credentials
API_KEY = "rUynbDAru4EfkUlKooBw7qIXWQhK1qnkltsFjGp3aB8GbAHe"

# Create temporary directory for saving audio
temp_dir = Path(tempfile.gettempdir()) / "hume_test"
temp_dir.mkdir(exist_ok=True)

# Test message
message = "This is a test notification. A trading opportunity has been detected for Apple at $195.67."
print(f"Generating speech for: '{message}'")

# Voice description
voice_description = "Professional trader voice with a clear, confident tone that sounds authoritative and calm."

try:
    # Initialize the Hume client
    print("Initializing Hume client...")
    client = HumeClient(api_key=API_KEY)
    
    # Make the API call
    print("Calling Hume AI API...")
    result = client.tts.synthesize_json(
        utterances=[
            PostedUtterance(
                text=message,
                description=voice_description,
            )
        ],
        format=FormatMp3(),
        num_generations=1,
    )
    
    # Print response to debug
    print(f"Response type: {type(result)}")
    print(f"Response attributes: {dir(result)}")
    
    # Get the first generation's audio from the response
    generation = result.generations[0]
    print(f"Generation data: {generation}")
    
    # Get audio data (base64 encoded)
    audio_base64 = generation.audio
    
    # Save audio to file
    temp_file = temp_dir / "test_notification.mp3"
    print(f"Saving audio to {temp_file}")
    with open(temp_file, "wb") as f:
        f.write(base64.b64decode(audio_base64))
    
    # Play the audio
    print("Playing audio...")
    pygame.mixer.music.load(str(temp_file))
    pygame.mixer.music.play()
    
    # Wait for playback to complete
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    print("Test completed successfully!")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
    
finally:
    # Clean up pygame
    pygame.mixer.quit() 