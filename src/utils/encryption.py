import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionManager:
    def __init__(self, password: str = None):
        """Initialize encryption manager with a password or default key"""
        if password is None:
            # Use a default password for this demo - in production, this should be user-provided
            password = "client_data_manager_default_key_2024"
        
        self.key = self._derive_key(password)
        self.fernet = Fernet(self.key)
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        # Salt should be stored securely - using a fixed salt for demo purposes
        salt = b'client_data_salt_2024_secure'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data and return base64 encoded result"""
        if not data:
            return ""
        
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            print(f"Encryption error: {e}")
            return data  # Return original data if encryption fails
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded data and return original string"""
        if not encrypted_data:
            return ""
        
        try:
            # Decode from base64 first
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            # Then decrypt
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return encrypted_data  # Return encrypted data if decryption fails


def generate_key() -> str:
    """Generate a new Fernet key"""
    key = Fernet.generate_key()
    return key.decode()


# Legacy functions for backward compatibility
def encrypt(data: str, key: str) -> bytes:
    """Legacy encrypt function"""
    fernet = Fernet(key.encode())
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data


def decrypt(encrypted_data: bytes, key: str) -> str:
    """Legacy decrypt function"""
    fernet = Fernet(key.encode())
    decrypted_data = fernet.decrypt(encrypted_data).decode()
    return decrypted_data