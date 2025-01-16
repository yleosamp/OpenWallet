from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import json
from typing import Optional

class SecurityManager:
    def __init__(self):
        self._key_file = 'wallet_key.key'
        self._salt_file = 'wallet_salt'
        self._encrypted_data_file = 'wallet_data.enc'
        
    def generate_key(self, password: str) -> None:
        salt = os.urandom(16)
        with open(self._salt_file, 'wb') as f:
            f.write(salt)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        with open(self._key_file, 'wb') as f:
            f.write(key)
            
    def encrypt_data(self, data: dict) -> None:
        with open(self._key_file, 'rb') as f:
            key = f.read()
            
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(json.dumps(data).encode())
        
        with open(self._encrypted_data_file, 'wb') as f:
            f.write(encrypted_data)
            
    def decrypt_data(self, password: str) -> Optional[dict]:
        try:
            with open(self._salt_file, 'rb') as f:
                salt = f.read()
                
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            with open(self._encrypted_data_file, 'rb') as f:
                encrypted_data = f.read()
                
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except:
            return None 