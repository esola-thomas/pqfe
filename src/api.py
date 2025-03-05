# Copyright (c) 2025 Ernesto Sola-Thomas
"""
API interface for the Post-Quantum File Encryption system.
Provides high-level functions for encryption, decryption, and key management.
"""

from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from .kyber_encryption import KyberEncryption
from . import key_management
from .symmetric import get_cipher_instance

class PQFEEncryptor:
    """
    Encryption-only interface for PQFE, initialized with only a public key.
    Cannot decrypt data as it doesn't have access to private keys.
    """
    
    def __init__(self, public_key: bytes, variant: str = "Kyber512", cipher: str = "AES256GCM"):
        """
        Initialize encryption-only PQFE with a public key.
        
        Args:
            public_key (bytes): Public key for encryption
            variant (str): Kyber variant to use (Kyber512, Kyber768, or Kyber1024)
            cipher (str): Symmetric cipher to use ("AES256GCM" or "ChaCha20Poly1305")
            
        Raises:
            ValueError: If the public_key is invalid or missing
        """
        if not isinstance(public_key, bytes) or len(public_key) < 10:
            raise ValueError("Invalid public key format or length")
            
        self.public_key = public_key
        self.variant = variant
        self.cipher = get_cipher_instance(cipher)

    def encrypt_data(self, data: bytes) -> Dict[str, Any]:
        """
        Encrypt data in-memory using the public key and a symmetric cipher.
        
        Args:
            data (bytes): Data to encrypt
            
        Returns:
            Dict containing:
            - encrypted_data (bytes): The encrypted data
            - ciphertext (bytes): The Kyber ciphertext
        """
        import oqs
        with oqs.KeyEncapsulation(self.variant) as kem:
            ciphertext, shared_secret = kem.encap_secret(self.public_key)
        encrypted_data = self.cipher.encrypt(data, shared_secret[:32])
        return {"encrypted_data": encrypted_data, "ciphertext": ciphertext}

    def encrypt_file(self, file_path: str, output_dir: Optional[str] = None, 
                     output_filename: Optional[str] = None, 
                     return_as_data: bool = False) -> Dict[str, Any]:
        """
        Encrypt a file using the public key and a symmetric cipher.
        
        Args:
            file_path (str): Path to the file to encrypt
            output_dir (Optional[str]): Directory to save the encrypted file
            output_filename (Optional[str]): Custom filename for the encrypted file
            return_as_data (bool): If True, return encrypted content as bytes instead of writing to disk
            
        Returns:
            Dict containing:
            - encrypted_file_path (str) if file written, or encrypted_data (bytes)
            - ciphertext (bytes): The Kyber ciphertext
        """
        from .file_ops import read_file, write_encrypted_file
        
        file_content = read_file(file_path)
        encrypt_result = self.encrypt_data(file_content)
        
        encrypted_content = encrypt_result["encrypted_data"]
        ciphertext = encrypt_result["ciphertext"]
        
        result = {'ciphertext': ciphertext}
        
        if return_as_data:
            result['encrypted_data'] = encrypted_content
        else:
            if output_filename is None:
                output_filename = file_path.split("/")[-1] + ".enc"
            if output_dir is None:
                output_dir = "/".join(file_path.split("/")[:-1])
            encrypted_file_path = write_encrypted_file(f"{output_dir}/{output_filename}", encrypted_content)
            result['encrypted_file_path'] = encrypted_file_path

        return result


class PQFE:
    """
    Main API interface for Post-Quantum File Encryption.
    """
    
    def __init__(self, variant: str = "Kyber512", key_directory: Optional[str] = None, cipher: str = "AES256GCM"):
        self.encryptor = KyberEncryption(variant=variant, cipher=cipher)
        self.key_directory = key_directory or str(Path.home() / ".pqfe" / "keys")
        
    def encrypt_file(self, file_path: str, public_key: Optional[bytes] = None, output_dir: Optional[str] = None, output_filename: Optional[str] = None, return_as_data: bool = False) -> Dict[str, Any]:
        return self.encryptor.encrypt_file(file_path, public_key, output_dir, output_filename, return_as_data)
        
    def decrypt_file(self, encrypted_file: str, ciphertext: bytes, private_key: Optional[bytes] = None, output_dir: Optional[str] = None, output_filename: Optional[str] = None, return_as_data: bool = False, encrypted_data: Optional[bytes] = None) -> Dict[str, Any]:
        if private_key is None:
            raise ValueError("Private key is required for decryption.")
        return self.encryptor.decrypt_file(encrypted_file, private_key, ciphertext, output_dir, output_filename, return_as_data, encrypted_data=encrypted_data)
        
    def generate_keys(self) -> Tuple[bytes, bytes]:
        public_key, private_key = self.encryptor.generate_keypair()
        key_management.save_keys(public_key, private_key, self.key_directory)
        return public_key, private_key
        
    def load_keys(self) -> Tuple[Optional[bytes], Optional[bytes]]:
        return key_management.load_keys(self.key_directory)
        
    def encrypt_data(self, data: bytes, public_key: bytes) -> Dict[str, Any]:
        """
        Encrypt data in-memory using Kyber key encapsulation and a symmetric cipher.
        """
        # Get the correct cipher name instead of using the class name
        cipher_name = self._get_cipher_name(self.encryptor.cipher)
        
        # Directly use oqs for encapsulation
        import oqs
        with oqs.KeyEncapsulation(self.encryptor.variant) as kem:
            ciphertext, shared_secret = kem.encap_secret(public_key)
        encrypted_data = self.encryptor.cipher.encrypt(data, shared_secret[:32])
        return {"encrypted_data": encrypted_data, "ciphertext": ciphertext, "shared_secret": shared_secret}
        
    def decrypt_data(self, encrypted_data: bytes, ciphertext: bytes, private_key: bytes) -> Dict[str, Any]:
        """
        Decrypt in-memory data using Kyber key encapsulation and the symmetric cipher.
        """
        import oqs
        with oqs.KeyEncapsulation(self.encryptor.variant, private_key) as kem:
            shared_secret = kem.decap_secret(ciphertext)
        decrypted_data = self.encryptor.cipher.decrypt(encrypted_data, shared_secret[:32])
        return {"decrypted_data": decrypted_data}
        
    def _get_cipher_name(self, cipher_instance) -> str:
        """
        Get the standardized cipher name from a cipher instance.
        
        Args:
            cipher_instance: Instance of a symmetric cipher
            
        Returns:
            str: Standardized cipher name (AES256GCM or ChaCha20Poly1305)
        """
        class_name = cipher_instance.__class__.__name__
        if "AES" in class_name:
            return "AES256GCM"
        elif "ChaCha" in class_name:
            return "ChaCha20Poly1305"
        else:
            # Default to AES if unknown
            return "AES256GCM"
    
    def create_encryptor(self, public_key: bytes) -> PQFEEncryptor:
        """
        Create an encryption-only interface using the provided public key.
        
        Args:
            public_key (bytes): Public key for encryption
            
        Returns:
            PQFEEncryptor: An object that can only encrypt data with the given public key
        """
        cipher_name = self._get_cipher_name(self.encryptor.cipher)
        
        return PQFEEncryptor(
            public_key=public_key, 
            variant=self.encryptor.variant, 
            cipher=cipher_name
        )