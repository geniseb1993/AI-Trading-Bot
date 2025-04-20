import os
import shutil
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureBackup:
    def __init__(self, backup_dir="secure_backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.key_file = self.backup_dir / "encryption_key.key"
        
    def generate_key(self, password):
        """Generate encryption key from password"""
        salt = b'salt_'  # In production, use a secure random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt_file(self, source_file, password):
        """Encrypt the source file"""
        key = self.generate_key(password)
        f = Fernet(key)
        
        with open(source_file, 'rb') as file:
            file_data = file.read()
        
        encrypted_data = f.encrypt(file_data)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        encrypted_file = self.backup_dir / f"env_backup_{timestamp}.encrypted"
        
        with open(encrypted_file, 'wb') as file:
            file.write(encrypted_data)
            
        return encrypted_file

    def decrypt_file(self, encrypted_file, password):
        """Decrypt the backup file"""
        key = self.generate_key(password)
        f = Fernet(key)
        
        with open(encrypted_file, 'rb') as file:
            encrypted_data = file.read()
            
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data

def backup_env(password):
    """Create an encrypted backup of the .env file"""
    backup_system = SecureBackup()
    source_env = Path(".env")
    
    if not source_env.exists():
        print("Error: .env file not found!")
        return
    
    try:
        encrypted_file = backup_system.encrypt_file(source_env, password)
        print(f"Successfully created encrypted backup at: {encrypted_file}")
        print("Please store this backup and the password in a secure location outside of the project directory.")
        
    except Exception as e:
        print(f"Error creating backup: {str(e)}")

if __name__ == "__main__":
    import getpass
    password = getpass.getpass("Enter a password to encrypt the backup: ")
    backup_env(password) 