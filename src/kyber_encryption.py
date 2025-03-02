# Copyright (c) 2025 Ernesto Sola-Thomas
"""
Main class for Kyber-based encryption operations.
Implements core encryption and decryption functionality using liboqs.
Now supports a pluggable symmetric cipher layer.
"""

from typing import Tuple, Dict, Any, Optional
import oqs
from .file_ops import read_file, write_encrypted_file, read_encrypted_file, write_decrypted_file
from .symmetric import get_cipher_instance

class KyberEncryption:
    """Main class for Kyber-based encryption operations"""

    SUPPORTED_VARIANTS = {
        "Kyber512": "Kyber512",
        "Kyber768": "Kyber768",
        "Kyber1024": "Kyber1024"
    }
    
    def __init__(self, variant: str = "Kyber512", cipher: str = "AES256GCM"):
        """
        Initialize KyberEncryption with specified variant and symmetric cipher.
        
        Args:
            variant (str): Kyber variant to use (Kyber512, Kyber768, or Kyber1024)
            cipher (str): Symmetric cipher to use ("AES256GCM" or "ChaCha20Poly1305")
        """
        if variant not in self.SUPPORTED_VARIANTS:
            raise ValueError(f"Unsupported variant. Choose from: {', '.join(self.SUPPORTED_VARIANTS.keys())}")
        self.variant = variant
        self.cipher_name = cipher
        self.cipher = get_cipher_instance(cipher)

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """
        Generate a new public/private key pair.
        
        Returns:
            Tuple[bytes, bytes]: (public_key, private_key)
        """
        with oqs.KeyEncapsulation(self.variant) as kem:
            public_key = kem.generate_keypair()
            private_key = kem.export_secret_key()
        return public_key, private_key

    def encrypt_file(
        self,
        input_file: str,
        public_key: Optional[bytes] = None,
        output_dir: Optional[str] = None,
        output_filename: Optional[str] = None,
        return_as_data: bool = False
    ) -> Dict[str, Any]:
        """
        Encrypt a file using Kyber and a symmetric cipher.
        
        Args:
            input_file (str): Path to the file to encrypt
            public_key (Optional[bytes]): Public key for encryption
            output_dir (Optional[str]): Directory to save the encrypted file; if None, use original location
            output_filename (Optional[str]): Custom filename for the encrypted file; defaults to input_file + '.enc'
            return_as_data (bool): If True, return encrypted content as bytes instead of writing to disk.
            
        Returns:
            Dict containing:
            - encrypted_file_path (str) if file written, or encrypted_data (bytes)
            - ciphertext (bytes): The Kyber ciphertext
            - shared_secret (bytes): The shared secret derived from key encapsulation
        """
        if public_key is None:
            raise ValueError("Public key is required for encryption.")

        file_content = read_file(input_file)

        with oqs.KeyEncapsulation(self.variant) as kem:
            ciphertext, shared_secret = kem.encap_secret(public_key)

        encrypted_content = self.cipher.encrypt(file_content, shared_secret[:32])
        
        result = {
            'ciphertext': ciphertext,
            'shared_secret': shared_secret
        }
        
        if return_as_data:
            result['encrypted_data'] = encrypted_content
        else:
            if output_filename is None:
                output_filename = input_file.split("/")[-1] + ".enc"
            if output_dir is None:
                output_dir = "/".join(input_file.split("/")[:-1])
            encrypted_file_path = write_encrypted_file(f"{output_dir}/{output_filename}", encrypted_content)
            result['encrypted_file_path'] = encrypted_file_path

        return result

    def decrypt_file(
        self,
        encrypted_file: str,
        private_key: bytes,
        ciphertext: bytes,
        output_dir: Optional[str] = None,
        output_filename: Optional[str] = None,
        return_as_data: bool = False
    ) -> Dict[str, Any]:
        """
        Decrypt a file using Kyber and a symmetric cipher.
        
        Args:
            encrypted_file (str): Path to the encrypted file
            private_key (bytes): Private key for decryption
            ciphertext (bytes): The Kyber ciphertext from encryption
            output_dir (Optional[str]): Directory to save the decrypted file; if None, use default behavior
            output_filename (Optional[str]): Custom filename for the decrypted file; defaults to removing '.enc'
            return_as_data (bool): If True, return decrypted content as bytes instead of writing to disk.
            
        Returns:
            Dict containing:
            - decrypted_file_path (str) if file written, or decrypted_data (bytes)
        """
        encrypted_content = read_encrypted_file(encrypted_file)

        with oqs.KeyEncapsulation(self.variant, private_key) as kem:
            shared_secret = kem.decap_secret(ciphertext)

        decrypted_content = self.cipher.decrypt(encrypted_content, shared_secret[:32])

        result = {}
        if return_as_data:
            result['decrypted_data'] = decrypted_content
        else:
            if output_filename is None:
                output_filename = encrypted_file.replace('.enc', '')
            if output_dir is None:
                output_dir = "/".join(encrypted_file.split("/")[:-1])
            decrypted_file_path = write_decrypted_file(f"{output_dir}/{output_filename}", decrypted_content)
            result['decrypted_file_path'] = decrypted_file_path

        return result
