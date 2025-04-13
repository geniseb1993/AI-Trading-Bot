"""
Notification Service Module

This module handles sending notifications for trade signals and alerts.
It supports multiple notification types including email, SMS, desktop, and voice alerts.
"""

import os
import logging
import smtplib
import requests
import platform
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional, Union
from plyer import notification
import pyttsx3
import json
from enum import Enum
from .hume_voice_service import HumeVoiceService, VoiceStyle

# Set up a logger for this module
logger = logging.getLogger(__name__)

class NotificationPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class NotificationGroup(Enum):
    TRADE = "trade"
    SYSTEM = "system"
    ALERT = "alert"
    ERROR = "error"

class NotificationTemplate:
    def __init__(self, name: str, subject: str, body: str):
        self.name = name
        self.subject = subject
        self.body = body

class NotificationService:
    """
    Service for sending notifications through various channels
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the notification service with configuration
        
        Args:
            config_path: Path to configuration file
        """
        # Set up logging first
        self._setup_logging()
        
        self.config = self._load_config(config_path)
        self.notification_settings = self.config.get("notification_settings", {})
        self.email_settings = self.notification_settings.get("email", {})
        self.sms_settings = self.notification_settings.get("sms", {})
        self.desktop_settings = self.notification_settings.get("desktop", {})
        self.voice_settings = self.notification_settings.get("voice", {})
        self.sound_settings = self.notification_settings.get("sound", {})
        self.templates = self._load_templates()
        self.notification_history = []
        
        # Initialize text-to-speech engines
        self.use_hume_ai = self.voice_settings.get("use_hume_ai", True)
        
        if self.use_hume_ai:
            try:
                self.hume_voice = HumeVoiceService(
                    api_key=self.voice_settings.get("hume_api_key"),
                    secret_key=self.voice_settings.get("hume_secret_key")
                )
                self.logger.info("Hume AI voice service initialized")
            except Exception as e:
                self.logger.error(f"Error initializing Hume AI voice service: {str(e)}")
                self.use_hume_ai = False
                self.engine = pyttsx3.init()
        else:
            self.engine = pyttsx3.init()
        
    def _setup_logging(self):
        """Set up logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("NotificationService")

    def _load_templates(self) -> Dict[str, NotificationTemplate]:
        """Load notification templates from templates directory"""
        templates = {}
        templates_dir = "templates/notifications"
        
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
            # Create default templates
            default_templates = {
                "trade_execution": NotificationTemplate(
                    "Trade Execution",
                    "Trade Executed: {symbol}",
                    "A {action} order for {symbol} has been executed at {price}"
                ),
                "system_alert": NotificationTemplate(
                    "System Alert",
                    "System Alert: {title}",
                    "{message}"
                ),
                "error": NotificationTemplate(
                    "Error",
                    "Error: {title}",
                    "{message}"
                )
            }
            for name, template in default_templates.items():
                self._save_template(name, template)
            return default_templates

        for filename in os.listdir(templates_dir):
            if filename.endswith(".json"):
                with open(os.path.join(templates_dir, filename), "r") as f:
                    data = json.load(f)
                    templates[data["name"]] = NotificationTemplate(
                        data["name"],
                        data["subject"],
                        data["body"]
                    )
        return templates

    def _save_template(self, name: str, template: NotificationTemplate):
        """Save a notification template to file"""
        templates_dir = "templates/notifications"
        os.makedirs(templates_dir, exist_ok=True)
        
        with open(os.path.join(templates_dir, f"{name}.json"), "w") as f:
            json.dump({
                "name": template.name,
                "subject": template.subject,
                "body": template.body
            }, f, indent=2)

    def send_notification(
        self,
        message: str,
        notification_type: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        group: NotificationGroup = NotificationGroup.SYSTEM,
        template_name: Optional[str] = None,
        template_data: Optional[Dict] = None,
        custom_sound: Optional[str] = None
    ) -> bool:
        """
        Send a notification using the specified type and template
        
        Args:
            message: The notification message
            notification_type: Type of notification (email, sms, desktop, voice)
            priority: Priority level of the notification
            group: Notification group
            template_name: Name of the template to use
            template_data: Data to fill in the template
            custom_sound: Path to custom sound file
        """
        try:
            # Get template if specified
            template = None
            if template_name and template_name in self.templates:
                template = self.templates[template_name]
                if template_data:
                    message = template.body.format(**template_data)

            # Create notification record
            notification_record = {
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "type": notification_type,
                "priority": priority.value,
                "group": group.value,
                "template": template_name,
                "status": "pending"
            }

            success = False
            if notification_type == "email":
                success = self.send_email_notification(message, priority, template)
            elif notification_type == "sms":
                success = self.send_sms_notification(message, priority)
            elif notification_type == "desktop":
                success = self.send_desktop_notification(message, priority, custom_sound)
            elif notification_type == "voice":
                success = self.send_voice_notification(message, priority)

            notification_record["status"] = "sent" if success else "failed"
            self.notification_history.append(notification_record)
            
            return success

        except Exception as e:
            self.logger.error(f"Error sending notification: {str(e)}")
            return False

    def send_email_notification(
        self,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        template: Optional[NotificationTemplate] = None
    ) -> bool:
        """Send email notification with priority and template support"""
        try:
            if not self.email_settings.get("enabled", False):
                return False

            msg = MIMEMultipart()
            msg["From"] = self.email_settings["sender_email"]
            msg["To"] = self.email_settings["recipient_email"]
            
            # Add priority to subject
            subject = f"[{priority.value.upper()}] "
            if template:
                subject += template.subject
            else:
                subject += "Notification"
            msg["Subject"] = subject

            # Format message body
            body = message
            if template:
                body = template.body.format(message=message)
            
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.email_settings["smtp_server"], self.email_settings["smtp_port"]) as server:
                server.starttls()
                server.login(self.email_settings["sender_email"], self.email_settings["password"])
                server.send_message(msg)

            return True

        except Exception as e:
            self.logger.error(f"Error sending email notification: {str(e)}")
            return False

    def send_sms_notification(
        self,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM
    ) -> bool:
        """Send SMS notification with priority support"""
        try:
            if not self.sms_settings.get("enabled", False):
                return False

            # Add priority indicator to message
            formatted_message = f"[{priority.value.upper()}] {message}"

            response = requests.post(
                self.sms_settings["api_endpoint"],
                json={
                    "to": self.sms_settings["phone_number"],
                    "message": formatted_message
                },
                headers={"Authorization": f"Bearer {self.sms_settings['api_key']}"}
            )

            return response.status_code == 200

        except Exception as e:
            self.logger.error(f"Error sending SMS notification: {str(e)}")
            return False

    def send_desktop_notification(
        self,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        custom_sound: Optional[str] = None
    ) -> bool:
        """Send desktop notification with priority and custom sound support"""
        try:
            if not self.desktop_settings.get("enabled", False):
                return False

            # Set notification timeout based on priority
            timeout = {
                NotificationPriority.HIGH: 10,
                NotificationPriority.MEDIUM: 5,
                NotificationPriority.LOW: 3
            }[priority]

            notification.notify(
                title=f"Trading Bot Alert [{priority.value.upper()}]",
                message=message,
                app_icon=None,
                timeout=timeout,
                toast=True
            )

            # Play custom sound if specified
            if custom_sound and os.path.exists(custom_sound):
                import winsound
                winsound.PlaySound(custom_sound, winsound.SND_FILENAME)

            return True

        except Exception as e:
            self.logger.error(f"Error sending desktop notification: {str(e)}")
            return False

    def send_voice_notification(
        self,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM
    ) -> bool:
        """Send voice notification with priority support"""
        try:
            if not self.voice_settings.get("enabled", False):
                return False

            # Choose between Hume AI and pyttsx3
            if self.use_hume_ai and hasattr(self, 'hume_voice'):
                # Use Hume AI for voice
                voice_style = VoiceStyle.PROFESSIONAL
                if priority == NotificationPriority.HIGH:
                    voice_style = VoiceStyle.URGENT
                elif priority == NotificationPriority.LOW:
                    voice_style = VoiceStyle.CASUAL
                    
                return self.hume_voice.speak(message, voice_style, priority.value)
            else:
                # Fallback to pyttsx3
                # Adjust voice properties based on priority
                if priority == NotificationPriority.HIGH:
                    self.engine.setProperty('rate', 200)
                    self.engine.setProperty('volume', 1.0)
                elif priority == NotificationPriority.MEDIUM:
                    self.engine.setProperty('rate', 150)
                    self.engine.setProperty('volume', 0.8)
                else:
                    self.engine.setProperty('rate', 100)
                    self.engine.setProperty('volume', 0.6)

                self.engine.say(message)
                self.engine.runAndWait()
                return True

        except Exception as e:
            self.logger.error(f"Error sending voice notification: {str(e)}")
            return False

    def get_notification_history(
        self,
        limit: int = 100,
        group: Optional[NotificationGroup] = None,
        priority: Optional[NotificationPriority] = None
    ) -> List[Dict]:
        """Get notification history with filtering options"""
        filtered_history = self.notification_history
        
        if group:
            filtered_history = [n for n in filtered_history if n["group"] == group.value]
        if priority:
            filtered_history = [n for n in filtered_history if n["priority"] == priority.value]
            
        return filtered_history[-limit:]

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from file"""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return {} 