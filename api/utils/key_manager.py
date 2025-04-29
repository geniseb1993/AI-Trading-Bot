"""
Secure Key Manager

Provides a secure interface for managing API keys and credentials with the following features:
- Encryption of keys at rest
- Safe key retrieval with access logging
- Environment-specific key management
- Key rotation policies
"""

import base64
import hashlib
import hmac
import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Configure logging
logger = logging.getLogger(__name__)

class KeyManager:
    """
    Secure key management system for storing and retrieving API keys and credentials.
    
    Features:
    - Secure encryption of keys
    - Access logging with audit trail
    - Key rotation policy enforcement
    - Environment-specific configurations
    """
    
    # Default key storage path
    DEFAULT_KEYS_FILE = "api/config/secure/keys.json"
    
    # Default encryption settings
    DEFAULT_SALT = b"AI_trading_bot_secure_salt"  # This would be stored securely in production
    MASTER_KEY_ENV_VAR = "API_KEY_ENCRYPTION_KEY"
    
    # Default key rotation policy (in days)
    DEFAULT_ROTATION_PERIOD = 90
    
    def __init__(self, 
        keys_file: Optional[str] = None, 
        master_key: Optional[str] = None,
        salt: Optional[bytes] = None,
        rotation_period: int = DEFAULT_ROTATION_PERIOD,
        environment: str = "development"
    ):
        """
        Initialize the key manager.
        
        Args:
            keys_file: Path to the keys storage file.
            master_key: Master encryption key (if not provided, will be loaded from environment).
            salt: Encryption salt (if not provided, will use default).
            rotation_period: Default key rotation period in days.
            environment: Current environment (development, testing, production).
        """
        self.keys_file = keys_file or self.DEFAULT_KEYS_FILE
        self.rotation_period = rotation_period
        self.environment = environment
        
        # Set up encryption
        self.salt = salt or self.DEFAULT_SALT
        self._setup_encryption(master_key)
        
        # Initialize keys storage
        self._initialize()
        
        logger.info(f"Key manager initialized with environment: {environment}")
    
    def _setup_encryption(self, master_key: Optional[str] = None) -> None:
        """
        Set up encryption with the master key.
        
        Args:
            master_key: Master encryption key.
        """
        # Get master key from parameter, environment, or generate one
        if master_key:
            self.master_key = master_key
        elif os.environ.get(self.MASTER_KEY_ENV_VAR):
            self.master_key = os.environ.get(self.MASTER_KEY_ENV_VAR)
        else:
            # For development only - in production, the key should be provided
            if self.environment == "production":
                raise ValueError(f"Master encryption key must be provided in production environment via {self.MASTER_KEY_ENV_VAR}")
            
            logger.warning("No master key provided or found in environment, generating temporary key")
            self.master_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        
        # Convert string master key to bytes if needed
        if isinstance(self.master_key, str):
            master_key_bytes = self.master_key.encode()
        else:
            master_key_bytes = self.master_key
        
        # Set up key derivation function
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        
        # Derive key and create Fernet cipher
        key = base64.urlsafe_b64encode(kdf.derive(master_key_bytes))
        self.cipher = Fernet(key)
    
    def _initialize(self) -> None:
        """
        Initialize the key storage system.
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.keys_file), exist_ok=True)
        
        # Load existing keys or create new storage
        if os.path.exists(self.keys_file):
            self._load_keys()
        else:
            self.keys = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "environment": self.environment
                },
                "services": {}
            }
            self._save_keys()
    
    def _load_keys(self) -> None:
        """
        Load and decrypt keys from storage.
        """
        try:
            with open(self.keys_file, "r") as f:
                encrypted_data = f.read().strip()
            
            if encrypted_data:
                # Decrypt data
                decrypted_data = self.cipher.decrypt(encrypted_data.encode()).decode()
                self.keys = json.loads(decrypted_data)
                
                # Update environment if different
                if self.keys.get("metadata", {}).get("environment") != self.environment:
                    logger.warning(f"Environment mismatch in keys file. File: {self.keys.get('metadata', {}).get('environment')}, Current: {self.environment}")
                    self.keys["metadata"]["environment"] = self.environment
                    self._save_keys()
            else:
                # Empty file, initialize new keys
                self.keys = {
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                        "environment": self.environment
                    },
                    "services": {}
                }
                self._save_keys()
        except Exception as e:
            logger.error(f"Failed to load keys: {str(e)}")
            # Initialize new keys on error
            self.keys = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "environment": self.environment
                },
                "services": {}
            }
    
    def _save_keys(self) -> None:
        """
        Encrypt and save keys to storage.
        """
        try:
            # Update timestamp
            self.keys["metadata"]["updated_at"] = datetime.now().isoformat()
            
            # Encrypt data
            data_json = json.dumps(self.keys, indent=2)
            encrypted_data = self.cipher.encrypt(data_json.encode()).decode()
            
            # Save to file
            with open(self.keys_file, "w") as f:
                f.write(encrypted_data)
        except Exception as e:
            logger.error(f"Failed to save keys: {str(e)}")
    
    def _log_access(self, service: str, key_name: str, action: str = "get") -> None:
        """
        Log key access for audit purposes.
        
        Args:
            service: Service name.
            key_name: Key name.
            action: Action performed (get, set, delete).
        """
        # Initialize logs if not present
        if "access_logs" not in self.keys:
            self.keys["access_logs"] = []
        
        # Add log entry with limited history (keep last 100 entries)
        self.keys["access_logs"].append({
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "key_name": key_name,
            "action": action,
            "environment": self.environment
        })
        
        # Limit log size
        if len(self.keys["access_logs"]) > 100:
            self.keys["access_logs"] = self.keys["access_logs"][-100:]
    
    def _check_rotation_needed(self, service: str, key_name: str) -> bool:
        """
        Check if key rotation is needed based on policy.
        
        Args:
            service: Service name.
            key_name: Key name.
            
        Returns:
            True if rotation is needed, False otherwise.
        """
        # Get key data
        service_keys = self.keys.get("services", {}).get(service, {})
        key_data = service_keys.get(key_name, {})
        
        # Check if rotation is needed
        if not key_data:
            return False
        
        # Get last rotation date
        last_rotation = key_data.get("last_rotation")
        if not last_rotation:
            return True
        
        # Parse last rotation date
        try:
            last_rotation_date = datetime.fromisoformat(last_rotation)
            rotation_due_date = last_rotation_date + timedelta(days=self.rotation_period)
            return datetime.now() >= rotation_due_date
        except (ValueError, TypeError):
            return True
    
    def set_key(self, service: str, key_name: str, key_value: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Set a key for a service.
        
        Args:
            service: Service name.
            key_name: Key name.
            key_value: Key value.
            metadata: Optional metadata about the key.
        """
        # Initialize service if not present
        if "services" not in self.keys:
            self.keys["services"] = {}
        
        if service not in self.keys["services"]:
            self.keys["services"][service] = {}
        
        # Set key with metadata
        self.keys["services"][service][key_name] = {
            "value": key_value,
            "created_at": datetime.now().isoformat(),
            "last_rotation": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Log access
        self._log_access(service, key_name, "set")
        
        # Save keys
        self._save_keys()
        
        logger.info(f"Key '{key_name}' set for service '{service}'")
    
    def get_key(self, service: str, key_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a key for a service.
        
        Args:
            service: Service name.
            key_name: Key name.
            default: Default value if key not found.
            
        Returns:
            Key value or default if not found.
        """
        # Check if service and key exist
        service_keys = self.keys.get("services", {}).get(service, {})
        key_data = service_keys.get(key_name, {})
        
        # Log access
        self._log_access(service, key_name, "get")
        
        # Check for rotation warning
        if key_data and self._check_rotation_needed(service, key_name):
            logger.warning(f"Key '{key_name}' for service '{service}' is due for rotation")
        
        # Return key value or default
        return key_data.get("value", default)
    
    def delete_key(self, service: str, key_name: str) -> bool:
        """
        Delete a key for a service.
        
        Args:
            service: Service name.
            key_name: Key name.
            
        Returns:
            True if key was deleted, False otherwise.
        """
        # Check if service and key exist
        if service in self.keys.get("services", {}) and key_name in self.keys["services"][service]:
            # Delete key
            del self.keys["services"][service][key_name]
            
            # Remove service if empty
            if not self.keys["services"][service]:
                del self.keys["services"][service]
            
            # Log access
            self._log_access(service, key_name, "delete")
            
            # Save keys
            self._save_keys()
            
            logger.info(f"Key '{key_name}' deleted for service '{service}'")
            return True
        else:
            logger.warning(f"Key '{key_name}' not found for service '{service}'")
            return False
    
    def rotate_key(self, service: str, key_name: str, new_key_value: str) -> bool:
        """
        Rotate a key for a service.
        
        Args:
            service: Service name.
            key_name: Key name.
            new_key_value: New key value.
            
        Returns:
            True if key was rotated, False otherwise.
        """
        # Check if service and key exist
        service_keys = self.keys.get("services", {}).get(service, {})
        key_data = service_keys.get(key_name, {})
        
        if not key_data:
            logger.warning(f"Key '{key_name}' not found for service '{service}'")
            return False
        
        # Store old key in history
        if "history" not in key_data:
            key_data["history"] = []
        
        key_data["history"].append({
            "value": key_data["value"],
            "rotated_at": datetime.now().isoformat()
        })
        
        # Limit history size
        if len(key_data["history"]) > 5:
            key_data["history"] = key_data["history"][-5:]
        
        # Update key value and rotation date
        key_data["value"] = new_key_value
        key_data["last_rotation"] = datetime.now().isoformat()
        
        # Log access
        self._log_access(service, key_name, "rotate")
        
        # Save keys
        self._save_keys()
        
        logger.info(f"Key '{key_name}' rotated for service '{service}'")
        return True
    
    def get_keys_for_service(self, service: str) -> Dict[str, str]:
        """
        Get all keys for a service.
        
        Args:
            service: Service name.
            
        Returns:
            Dictionary of key names and values.
        """
        # Get service keys
        service_keys = self.keys.get("services", {}).get(service, {})
        
        # Extract key values
        result = {}
        for key_name, key_data in service_keys.items():
            result[key_name] = key_data.get("value")
            
            # Check for rotation warning
            if self._check_rotation_needed(service, key_name):
                logger.warning(f"Key '{key_name}' for service '{service}' is due for rotation")
            
            # Log access
            self._log_access(service, key_name, "get")
        
        return result
    
    def get_services(self) -> List[str]:
        """
        Get all service names.
        
        Returns:
            List of service names.
        """
        return list(self.keys.get("services", {}).keys())
    
    def get_key_names(self, service: str) -> List[str]:
        """
        Get all key names for a service.
        
        Args:
            service: Service name.
            
        Returns:
            List of key names.
        """
        service_keys = self.keys.get("services", {}).get(service, {})
        return list(service_keys.keys())
    
    def get_access_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get access logs.
        
        Args:
            limit: Maximum number of logs to return.
            
        Returns:
            List of access logs.
        """
        logs = self.keys.get("access_logs", [])
        return logs[-limit:]
    
    def import_keys(self, data: Dict[str, Any], overwrite: bool = False) -> int:
        """
        Import keys from data.
        
        Args:
            data: Key data to import.
            overwrite: Whether to overwrite existing keys.
            
        Returns:
            Number of keys imported.
        """
        count = 0
        
        for service, keys in data.items():
            for key_name, key_value in keys.items():
                # Check if key exists
                service_keys = self.keys.get("services", {}).get(service, {})
                key_exists = key_name in service_keys
                
                # Skip if key exists and not overwriting
                if key_exists and not overwrite:
                    continue
                
                # Set key
                self.set_key(service, key_name, key_value)
                count += 1
        
        return count
    
    def export_keys(self, services: Optional[List[str]] = None) -> Dict[str, Dict[str, str]]:
        """
        Export keys as data.
        
        Args:
            services: Optional list of services to export.
            
        Returns:
            Dictionary of services and keys.
        """
        result = {}
        
        # Get services to export
        if services is None:
            services = self.get_services()
        
        # Export keys for each service
        for service in services:
            result[service] = self.get_keys_for_service(service)
        
        return result
    
    def generate_hmac(self, service: str, key_name: str, message: str) -> Optional[str]:
        """
        Generate HMAC signature using a stored key.
        
        Args:
            service: Service name.
            key_name: Key name.
            message: Message to sign.
            
        Returns:
            HMAC signature or None if key not found.
        """
        # Get key
        key = self.get_key(service, key_name)
        
        if not key:
            logger.warning(f"Key '{key_name}' not found for service '{service}'")
            return None
        
        # Generate HMAC
        key_bytes = key.encode()
        message_bytes = message.encode()
        
        hmac_signature = hmac.new(key_bytes, message_bytes, hashlib.sha256).hexdigest()
        return hmac_signature
    
    def validate_hmac(self, service: str, key_name: str, message: str, signature: str) -> bool:
        """
        Validate HMAC signature using a stored key.
        
        Args:
            service: Service name.
            key_name: Key name.
            message: Message that was signed.
            signature: HMAC signature to validate.
            
        Returns:
            True if signature is valid, False otherwise.
        """
        # Generate HMAC for comparison
        expected_signature = self.generate_hmac(service, key_name, message)
        
        if not expected_signature:
            return False
        
        # Compare signatures (constant time comparison)
        return hmac.compare_digest(expected_signature, signature)

# Singleton instance
_key_manager = None

def get_key_manager(
    keys_file: Optional[str] = None, 
    master_key: Optional[str] = None,
    environment: Optional[str] = None
) -> KeyManager:
    """
    Get or create the key manager singleton instance.
    
    Args:
        keys_file: Path to the keys storage file.
        master_key: Master encryption key.
        environment: Current environment.
        
    Returns:
        KeyManager instance.
    """
    global _key_manager
    
    # Create instance if not exists
    if _key_manager is None:
        # Determine environment
        if environment is None:
            environment = os.environ.get("ENV", "development")
        
        _key_manager = KeyManager(
            keys_file=keys_file,
            master_key=master_key,
            environment=environment
        )
    
    return _key_manager 