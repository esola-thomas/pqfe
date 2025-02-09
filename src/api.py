# Copyright (c) 2025 Ernesto Sola-Thomas

"""
API interface for the Post-Quantum File Encryption system.
Provides high-level functions for encryption, decryption, and key management.
"""

from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from .kyber_encryption import KyberEncryption
from . import key_management

class PQFE:
    """Main API interface for Post-Quantum File Encryption"""
    
    def __init__(self, variant: str = "Kyber512", key_directory: Optional[str] = None):
        """
        Initialize PQFE with specified Kyber variant and key directory.
        
        Args:
            variant (str): Kyber variant to use
            key_directory (Optional[str]): Directory for key storage
        """
        self.encryptor = KyberEncryption(variant=variant)
        self.key_directory = key_directory or str(Path.home() / ".pqfe" / "keys")
        
    def encrypt_file(self, file_path: str, public_key: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Encrypt a file using Kyber.
        
        Args:
            file_path (str): Path to file to encrypt
            public_key (Optional[bytes]): Public key for encryption
            
        Returns:
            Dict containing encryption results
        """
        return self.encryptor.encrypt_file(file_path, public_key)
        
    def decrypt_file(
        self,
        encrypted_file: str,
        private_key: Optional[bytes] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Decrypt a file using Kyber.
        
        Args:
            encrypted_file (str): Path to encrypted file
            private_key (Optional[bytes]): Private key for decryption
            output_path (Optional[str]): Custom output path
            
        Returns:
            str: Path to decrypted file
        """
        if private_key is None:
            raise ValueError("Private key is required for decryption.")
        decrypted_content = self.encryptor.decrypt_file(encrypted_file, private_key)
        if output_path is None:
            output_path = encrypted_file.replace('.enc', '')
        with open(output_path, 'wb') as f:
            f.write(decrypted_content)
        return output_path
        
    def generate_keys(self) -> Tuple[bytes, bytes]:
        """
        Generate new keypair and save to configured directory.
        
        Returns:
            Tuple[bytes, bytes]: (public_key, private_key)
        """
        public_key, private_key = self.encryptor.generate_keypair()
        key_dir = Path(self.key_directory)
        key_dir.mkdir(parents=True, exist_ok=True)
        with open(key_dir / 'public_key.pem', 'wb') as f:
            f.write(public_key)
        with open(key_dir / 'private_key.pem', 'wb') as f:
            f.write(private_key)
        return public_key, private_key
        
    def load_keys(self) -> Tuple[Optional[bytes], Optional[bytes]]:
        """
        Load keys from configured directory.
        
        Returns:
            Tuple[Optional[bytes], Optional[bytes]]: (public_key, private_key)
        """
        key_dir = Path(self.key_directory)
        try:
            with open(key_dir / 'public_key.pem', 'rb') as f:
                public_key = f.read()
            with open(key_dir / 'private_key.pem', 'rb') as f:
                private_key = f.read()
            return public_key, private_key
        except FileNotFoundError:
            return None, None 