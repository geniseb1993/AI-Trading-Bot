"""
Credentials Manager

Provides secure storage and retrieval of API keys and credentials.
Supports encryption, key rotation, and environment-based configuration.
"""

import base64
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Configure logging
logger = logging.getLogger(__name__)

class CredentialsError(Exception):
    """Base exception for credential-related errors."""
    pass

class CredentialNotFoundError(CredentialsError):
    """Exception raised when a credential is not found."""
    pass

class EncryptionError(CredentialsError):
    """Exception raised when there's an encryption/decryption error."""
    pass

class CredentialsManager:
    """
    Secure manager for API credentials and keys.
    
    Features:
    - Encrypted storage of credentials
    - Environment-based configuration
    - Key rotation support
    - Secure memory handling
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Create a singleton instance."""
        if cls._instance is None:
            cls._instance = super(CredentialsManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(
        self, 
        credentials_file: Optional[str] = None,
        master_key_env_var: str = "API_MASTER_KEY",
        auto_save: bool = True,
        salt: Optional[bytes] = None
    ):
        """
        Initialize the credentials manager.
        
        Args:
            credentials_file: Path to the credentials file. Default is './api/config/credentials.json'.
            master_key_env_var: Environment variable name for the master encryption key.
            auto_save: Whether to automatically save changes to the credentials file.
            salt: Salt for key derivation. Random if not provided.
        """
        if getattr(self, "_initialized", False):
            return
            
        self._credentials_file = credentials_file or os.path.join("api", "config", "credentials.json")
        self._master_key_env_var = master_key_env_var
        self._auto_save = auto_save
        self._credentials: Dict[str, Dict[str, Any]] = {}
        self._encrypted = False
        self._salt = salt or os.urandom(16)
        self._cipher = None
        
        # Load credentials if file exists
        self._load()
        
        self._initialized = True
    
    def _get_master_key(self) -> bytes:
        """
        Get the master encryption key from the environment.
        
        Returns:
            Master key as bytes.
            
        Raises:
            EncryptionError: If the master key is not found.
        """
        master_key = os.environ.get(self._master_key_env_var)
        
        if not master_key:
            raise EncryptionError(f"Master key not found in environment variable {self._master_key_env_var}")
        
        # Convert string to bytes if necessary
        if isinstance(master_key, str):
            master_key = master_key.encode()
        
        return master_key
    
    def _init_cipher(self) -> None:
        """
        Initialize the encryption cipher.
        
        Raises:
            EncryptionError: If the cipher initialization fails.
        """
        try:
            master_key = self._get_master_key()
            
            # Derive a key from the master key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self._salt,
                iterations=480000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(master_key))
            self._cipher = Fernet(key)
        except Exception as e:
            raise EncryptionError(f"Failed to initialize encryption cipher: {str(e)}")
    
    def _encrypt(self, data: str) -> str:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt.
            
        Returns:
            Encrypted data as string.
            
        Raises:
            EncryptionError: If encryption fails.
        """
        if self._cipher is None:
            self._init_cipher()
            
        try:
            return self._cipher.encrypt(data.encode()).decode()
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    def _decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Encrypted data to decrypt.
            
        Returns:
            Decrypted data as string.
            
        Raises:
            EncryptionError: If decryption fails.
        """
        if self._cipher is None:
            self._init_cipher()
            
        try:
            return self._cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            raise EncryptionError(f"Decryption failed: {str(e)}")
    
    def _load(self) -> None:
        """
        Load credentials from file.
        
        Raises:
            EncryptionError: If decryption fails.
        """
        if not os.path.exists(self._credentials_file):
            self._credentials = {}
            return
            
        try:
            with open(self._credentials_file, "r") as f:
                data = json.load(f)
                
            # Check if data is encrypted
            if data.get("_encrypted", False):
                if self._cipher is None:
                    self._init_cipher()
                    
                encrypted_data = data.get("data", "")
                decrypted_data = self._decrypt(encrypted_data)
                self._credentials = json.loads(decrypted_data)
                self._encrypted = True
                
                # Store salt
                if "salt" in data:
                    self._salt = base64.b64decode(data["salt"])
            else:
                self._credentials = data
                self._encrypted = False
        except Exception as e:
            logger.error(f"Failed to load credentials: {str(e)}")
            self._credentials = {}
    
    def save(self) -> None:
        """
        Save credentials to file.
        
        Raises:
            EncryptionError: If encryption fails.
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self._credentials_file), exist_ok=True)
        
        try:
            if self._encrypted:
                # Encrypt credentials
                if self._cipher is None:
                    self._init_cipher()
                    
                credentials_json = json.dumps(self._credentials)
                encrypted_data = self._encrypt(credentials_json)
                
                data = {
                    "_encrypted": True,
                    "salt": base64.b64encode(self._salt).decode(),
                    "version": 1,
                    "timestamp": int(time.time()),
                    "data": encrypted_data
                }
            else:
                data = self._credentials
                
            with open(self._credentials_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save credentials: {str(e)}")
            raise EncryptionError(f"Failed to save credentials: {str(e)}")
    
    def enable_encryption(self) -> None:
        """
        Enable encryption for credentials.
        
        Raises:
            EncryptionError: If encryption fails.
        """
        if not self._encrypted:
            self._encrypted = True
            
            if self._auto_save:
                self.save()
    
    def disable_encryption(self) -> None:
        """
        Disable encryption for credentials.
        
        Raises:
            EncryptionError: If decryption fails.
        """
        if self._encrypted:
            self._encrypted = False
            
            if self._auto_save:
                self.save()
    
    def set(self, 
        service: str, 
        key: str, 
        value: Any, 
        save: Optional[bool] = None
    ) -> None:
        """
        Set a credential value.
        
        Args:
            service: Service name.
            key: Credential key.
            value: Credential value.
            save: Whether to save changes to file. Default is auto_save value.
            
        Raises:
            EncryptionError: If saving fails.
        """
        if service not in self._credentials:
            self._credentials[service] = {}
            
        self._credentials[service][key] = value
        
        if save or (save is None and self._auto_save):
            self.save()
    
    def get(self, 
        service: str, 
        key: str, 
        default: Any = None
    ) -> Any:
        """
        Get a credential value.
        
        Args:
            service: Service name.
            key: Credential key.
            default: Default value if credential is not found.
            
        Returns:
            Credential value or default.
            
        Raises:
            CredentialNotFoundError: If credential is not found and no default is provided.
        """
        if service not in self._credentials or key not in self._credentials[service]:
            if default is not None:
                return default
            raise CredentialNotFoundError(f"Credential '{key}' for service '{service}' not found")
            
        return self._credentials[service][key]
    
    def has(self, service: str, key: str) -> bool:
        """
        Check if a credential exists.
        
        Args:
            service: Service name.
            key: Credential key.
            
        Returns:
            True if credential exists, False otherwise.
        """
        return service in self._credentials and key in self._credentials[service]
    
    def delete(self, 
        service: str, 
        key: str, 
        save: Optional[bool] = None
    ) -> bool:
        """
        Delete a credential.
        
        Args:
            service: Service name.
            key: Credential key.
            save: Whether to save changes to file. Default is auto_save value.
            
        Returns:
            True if credential was deleted, False if it didn't exist.
            
        Raises:
            EncryptionError: If saving fails.
        """
        if service in self._credentials and key in self._credentials[service]:
            del self._credentials[service][key]
            
            # Remove service if no credentials left
            if not self._credentials[service]:
                del self._credentials[service]
                
            if save or (save is None and self._auto_save):
                self.save()
                
            return True
            
        return False
    
    def get_service(self, service: str) -> Dict[str, Any]:
        """
        Get all credentials for a service.
        
        Args:
            service: Service name.
            
        Returns:
            Dictionary of credentials for the service.
        """
        return self._credentials.get(service, {}).copy()
    
    def get_services(self) -> List[str]:
        """
        Get list of services.
        
        Returns:
            List of service names.
        """
        return list(self._credentials.keys())
    
    def clear(self, save: Optional[bool] = None) -> None:
        """
        Clear all credentials.
        
        Args:
            save: Whether to save changes to file. Default is auto_save value.
            
        Raises:
            EncryptionError: If saving fails.
        """
        self._credentials = {}
        
        if save or (save is None and self._auto_save):
            self.save()
    
    def rotate_master_key(self, new_master_key: str) -> None:
        """
        Rotate the master encryption key.
        
        Args:
            new_master_key: New master key.
            
        Raises:
            EncryptionError: If key rotation fails.
        """
        # Save current credentials with previous key
        current_credentials = self._credentials.copy()
        
        # Update master key in environment
        os.environ[self._master_key_env_var] = new_master_key
        
        # Generate new salt
        self._salt = os.urandom(16)
        
        # Reset cipher to use new key and salt
        self._cipher = None
        self._init_cipher()
        
        # Restore credentials and save with new key
        self._credentials = current_credentials
        self.save()
        
# Convenience function to get the credentials manager instance
def get_credentials_manager(
    credentials_file: Optional[str] = None,
    master_key_env_var: str = "API_MASTER_KEY",
    auto_save: bool = True
) -> CredentialsManager:
    """
    Get the singleton credentials manager instance.
    
    Args:
        credentials_file: Path to the credentials file. Default is './api/config/credentials.json'.
        master_key_env_var: Environment variable name for the master encryption key.
        auto_save: Whether to automatically save changes to the credentials file.
        
    Returns:
        CredentialsManager instance.
    """
    return CredentialsManager(
        credentials_file=credentials_file,
        master_key_env_var=master_key_env_var,
        auto_save=auto_save
    ) 