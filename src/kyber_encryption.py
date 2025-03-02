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

    def encrypt_file(self, file_path, public_key, output_file=None, return_as_data=False):
        """
        Encrypt a file using Kyber and symmetric encryption.
        
        Args:
            file_path: Path to the file to encrypt
            public_key: Kyber public key
            output_file: Path to save encrypted file (optional)
            return_as_data: Return the encrypted data rather than saving to file
            
        Returns:
            Dict with encryption results including ciphertext, file path, and optionally encrypted data
        """
        # Read the file content
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Generate a shared secret
        shared_secret, ciphertext = self.kyber.encapsulate(public_key)
        
        # Encrypt the file content
        encrypted_content = self.cipher.encrypt(file_content, shared_secret[:32])
        
        # Store the encrypted content for potential in-memory operations later
        self._encrypted_content = encrypted_content
        
        result = {
            'ciphertext': ciphertext,
            'shared_secret': shared_secret,
        }
        
        if return_as_data:
            result['encrypted_data'] = encrypted_content
            return result
        
        # Determine output path
        if not output_file:
            output_file = f"{file_path}.encrypted"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Write encrypted content to file
        with open(output_file, 'wb') as f:
            f.write(encrypted_content)
        
        result['encrypted_file_path'] = output_file
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

    def decrypt_file(self, encrypted_file, private_key, ciphertext=None, output_file=None, return_as_data=False):
        """
        Decrypt a file using Kyber and symmetric decryption
        
        Args:
            encrypted_file: Path to the encrypted file or reference filename
            private_key: Kyber private key
            ciphertext: Kyber ciphertext (if already available)
            output_file: Path to save decrypted file (optional)
            return_as_data: Return the decrypted data rather than saving to file
            
        Returns:
            If return_as_data is True, returns the decrypted bytes.
            Otherwise, returns a dict with the decrypted file path.
        """
        # Get the shared secret from the Kyber ciphertext
        shared_secret = self.kyber.decapsulate(ciphertext, private_key)
        
        # Read the encrypted file content if needed
        if not return_as_data and os.path.exists(encrypted_file):
            with open(encrypted_file, 'rb') as f:
                encrypted_content = f.read()
        else:
            # This handles the case where we're just using the filename for reference
            # but the actual encrypted content is passed separately
            if hasattr(self, '_encrypted_content') and self._encrypted_content:
                encrypted_content = self._encrypted_content
            else:
                raise ValueError("Encrypted content not available and file does not exist")
        
        # Decrypt the content using the shared secret
        decrypted_content = self.cipher.decrypt(encrypted_content, shared_secret[:32])
        
        if return_as_data:
            return decrypted_content
        
        # Determine output path
        if not output_file:
            # Default to original location without '.encrypted' extension
            if encrypted_file.endswith('.encrypted'):
                output_file = encrypted_file[:-10]
            else:
                # Create a new filename with .decrypted extension
                output_file = f"{encrypted_file}.decrypted"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Write decrypted content to file
        with open(output_file, 'wb') as f:
            f.write(decrypted_content)
        
        return {'decrypted_file_path': output_file}
