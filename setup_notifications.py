"""
Setup script for notification system dependencies.
This script installs all required dependencies for the notification system,
including Hume AI voice service and pygame for audio playback.
"""

import os
import sys
import platform
import subprocess
import json

def run_command(command):
    """Run a command and print output"""
    print(f"Running: {command}")
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if stdout:
            print(stdout.decode())
        if stderr:
            print(stderr.decode())
            
        return process.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def install_requirements():
    """Install Python dependencies from requirements.txt"""
    print("Installing required Python packages...")
    return run_command(f"{sys.executable} -m pip install -r requirements.txt")

def configure_notifications():
    """Configure notification settings"""
    print("Configuring notification settings...")
    
    # Default config file path
    config_path = "config.json"
    config = {}
    
    # Load existing config if it exists
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Add notification settings if not present
    if "notification_settings" not in config:
        config["notification_settings"] = {}
    
    notification_settings = config["notification_settings"]
    
    # Configure voice settings
    if "voice" not in notification_settings:
        notification_settings["voice"] = {}
    
    voice_settings = notification_settings["voice"]
    voice_settings["enabled"] = True
    voice_settings["use_hume_ai"] = True
    voice_settings["hume_api_key"] = os.environ.get("HUME_API_KEY", "rUynbDAru4EfkUlKooBw7qIXWQhK1qnkltsFjGp3aB8GbAHe")
    voice_settings["hume_secret_key"] = os.environ.get("HUME_SECRET_KEY", "SkDtniP54WL0hcMyjysr8v4D0owoL4omZQ8bmKBoA70Til3wI6BvUM6ToIGZL3hr")
    
    # Configure desktop notification settings
    if "desktop" not in notification_settings:
        notification_settings["desktop"] = {}
    
    desktop_settings = notification_settings["desktop"]
    desktop_settings["enabled"] = True
    
    # Save config
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {config_path}")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def test_hume_voice():
    """Test the Hume AI voice service"""
    print("Testing Hume AI voice service...")
    return run_command(f"{sys.executable} test_hume_voice.py")

def main():
    """Main setup function"""
    print("=" * 50)
    print("Notification System Setup")
    print("=" * 50)
    
    # Install requirements
    print("\nStep 1: Installing requirements")
    if not install_requirements():
        print("Error installing requirements. Please check the error messages above.")
        return
    
    # Configure notification settings
    print("\nStep 2: Configuring notification settings")
    if not configure_notifications():
        print("Error configuring notification settings. Please check the error messages above.")
        return
    
    # Test Hume voice
    print("\nStep 3: Testing Hume AI voice (optional)")
    response = input("Would you like to test the Hume AI voice service? (y/n): ")
    if response.lower() == 'y':
        if not test_hume_voice():
            print("Error testing Hume AI voice. Please check the error messages above.")
    
    print("\nSetup completed successfully! The notification system is now configured to use:")
    print("- Desktop notifications for real-time trading alerts")
    print("- Hume AI voice notifications for high-priority alerts")
    print("\nYou can further customize notification settings in the frontend settings panel.")

if __name__ == "__main__":
    main() 