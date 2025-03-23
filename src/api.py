# Copyright (c) 2025 Ernesto Sola-Thomas
"""
API interface for the Post-Quantum File Encryption system.
Provides high-level functions for encryption, decryption, and key management.
"""
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from .kyber_encryption import KyberEncryption
from .dilithium_signatures import DilithiumSignature
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

class PQFESigner:
    """
    Signing-only interface for PQFE, initialized with a signing private key.
    Used for digital signatures using Dilithium.
    """
    
    def __init__(self, private_key: bytes, variant: str = "Dilithium3"):
        """
        Initialize signing-only PQFE with a private key.
        
        Args:
            private_key (bytes): Private key for signing
            variant (str): Dilithium variant to use (Dilithium2, Dilithium3, or Dilithium5)
            
        Raises:
            ValueError: If the private_key is invalid or missing
        """
        if not isinstance(private_key, bytes) or len(private_key) < 10:
            raise ValueError("Invalid private key format or length")
            
        self.private_key = private_key
        self.variant = variant
        self.signer = DilithiumSignature(variant=variant)
        
    def sign_data(self, data: bytes) -> bytes:
        """
        Sign data using the private key.
        
        Args:
            data (bytes): Data to sign
            
        Returns:
            bytes: Digital signature
        """
        return self.signer.sign_data(data, self.private_key)
        
    def sign_file(self, file_path: str) -> bytes:
        """
        Sign a file using the private key.
        
        Args:
            file_path (str): Path to the file to sign
            
        Returns:
            bytes: Digital signature
        """
        return self.signer.sign_file(file_path, self.private_key)

class PQFEVerifier:
    """
    Verification-only interface for PQFE, initialized with a signature public key.
    Used for verifying digital signatures using Dilithium.
    """
    
    def __init__(self, public_key: bytes, variant: str = "Dilithium3"):
        """
        Initialize verification-only PQFE with a public key.
        
        Args:
            public_key (bytes): Public key for verification
            variant (str): Dilithium variant to use (Dilithium2, Dilithium3, or Dilithium5)
            
        Raises:
            ValueError: If the public_key is invalid or missing
        """
        if not isinstance(public_key, bytes) or len(public_key) < 10:
            raise ValueError("Invalid public key format or length")
            
        self.public_key = public_key
        self.variant = variant
        self.verifier = DilithiumSignature(variant=variant)
        
    def verify_data(self, data: bytes, signature: bytes) -> bool:
        """
        Verify data signature using the public key.
        
        Args:
            data (bytes): Data to verify
            signature (bytes): Signature to verify
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        return self.verifier.verify_signature(data, signature, self.public_key)
        
    def verify_file(self, file_path: str, signature: bytes) -> bool:
        """
        Verify a file's signature using the public key.
        
        Args:
            file_path (str): Path to the file to verify
            signature (bytes): Signature to verify
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        return self.verifier.verify_file(file_path, signature, self.public_key)

class PQFE:
    """
    Main API interface for Post-Quantum File Encryption.
    """
    
    def __init__(self, kyber_variant: str = "Kyber512", dilithium_variant: str = "Dilithium3", 
                 key_directory: Optional[str] = None, cipher: str = "AES256GCM"):
        self.encryptor = KyberEncryption(variant=kyber_variant, cipher=cipher)
        self.signer = DilithiumSignature(variant=dilithium_variant)
        self.key_directory = key_directory or str(Path.home() / ".pqfe" / "keys")
        self.kyber_variant = kyber_variant
        self.dilithium_variant = dilithium_variant
        
    def encrypt_file(self, file_path: str, public_key: Optional[bytes] = None, 
                     output_dir: Optional[str] = None, output_filename: Optional[str] = None, 
                     return_as_data: bool = False) -> Dict[str, Any]:
        return self.encryptor.encrypt_file(file_path, public_key, output_dir, output_filename, return_as_data)
        
    def decrypt_file(self, encrypted_file: str, ciphertext: bytes, private_key: Optional[bytes] = None, 
                     output_dir: Optional[str] = None, output_filename: Optional[str] = None, 
                     return_as_data: bool = False, encrypted_data: Optional[bytes] = None) -> Dict[str, Any]:
        if private_key is None:
            raise ValueError("Private key is required for decryption.")
        return self.encryptor.decrypt_file(encrypted_file, private_key, ciphertext, output_dir, output_filename, return_as_data, encrypted_data=encrypted_data)
        
    def generate_encryption_keys(self) -> Tuple[bytes, bytes]:
        """
        Generate a new Kyber public/private key pair for encryption.
        
        Returns:
            Tuple[bytes, bytes]: (public_key, private_key)
        """
        public_key, private_key = self.encryptor.generate_keypair()
        key_management.save_keys(public_key, private_key, self.key_directory, key_type="encryption")
        return public_key, private_key
    
    def generate_signature_keys(self) -> Tuple[bytes, bytes]:
        """
        Generate a new Dilithium public/private key pair for digital signatures.
        
        Returns:
            Tuple[bytes, bytes]: (public_key, private_key)
        """
        public_key, private_key = self.signer.generate_keypair()
        key_management.save_keys(public_key, private_key, self.key_directory, key_type="signature")
        return public_key, private_key
        
    def generate_keys(self) -> Tuple[bytes, bytes]:
        """
        Generate a new Kyber public/private key pair for encryption.
        This is kept for backward compatibility.
        
        Returns:
            Tuple[bytes, bytes]: (public_key, private_key)
        """
        return self.generate_encryption_keys()
        
    def load_encryption_keys(self) -> Tuple[Optional[bytes], Optional[bytes]]:
        """
        Load Kyber encryption keys from storage.
        
        Returns:
            Tuple[Optional[bytes], Optional[bytes]]: (public_key, private_key)
        """
        return key_management.load_keys(self.key_directory, key_type="encryption")
    
    def load_signature_keys(self) -> Tuple[Optional[bytes], Optional[bytes]]:
        """
        Load Dilithium signature keys from storage.
        
        Returns:
            Tuple[Optional[bytes], Optional[bytes]]: (public_key, private_key)
        """
        return key_management.load_keys(self.key_directory, key_type="signature")
        
    def load_keys(self) -> Tuple[Optional[bytes], Optional[bytes]]:
        """
        Load Kyber encryption keys from storage.
        This is kept for backward compatibility.
        
        Returns:
            Tuple[Optional[bytes], Optional[bytes]]: (public_key, private_key)
        """
        return self.load_encryption_keys()
        
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
    
    def sign_data(self, data: bytes, private_key: bytes) -> bytes:
        """
        Sign data using Dilithium digital signature.
        
        Args:
            data (bytes): Data to sign
            private_key (bytes): Private key for signing
            
        Returns:
            bytes: Digital signature
        """
        return self.signer.sign_data(data, private_key)
    
    def verify_data(self, data: bytes, signature: bytes, public_key: bytes) -> bool:
        """
        Verify data signature using Dilithium digital signature.
        
        Args:
            data (bytes): Data to verify
            signature (bytes): Signature to verify
            public_key (bytes): Public key for verification
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        return self.signer.verify_signature(data, signature, public_key)
    
    def sign_file(self, file_path: str, private_key: bytes) -> bytes:
        """
        Sign a file using Dilithium digital signature.
        
        Args:
            file_path (str): Path to the file to sign
            private_key (bytes): Private key for signing
            
        Returns:
            bytes: Digital signature
        """
        return self.signer.sign_file(file_path, private_key)
    
    def verify_file(self, file_path: str, signature: bytes, public_key: bytes) -> bool:
        """
        Verify a file's signature using Dilithium digital signature.
        
        Args:
            file_path (str): Path to the file to verify
            signature (bytes): Signature to verify
            public_key (bytes): Public key for verification
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        return self.signer.verify_file(file_path, signature, public_key)
        
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
        
    def create_signer(self, private_key: bytes) -> PQFESigner:
        """
        Create a signing-only interface using the provided private key.
        
        Args:
            private_key (bytes): Private key for signing
            
        Returns:
            PQFESigner: An object that can only sign data with the given private key
        """
        return PQFESigner(
            private_key=private_key,
            variant=self.dilithium_variant
        )
        
    def create_verifier(self, public_key: bytes) -> PQFEVerifier:
        """
        Create a verification-only interface using the provided public key.
        
        Args:
            public_key (bytes): Public key for verification
            
        Returns:
            PQFEVerifier: An object that can only verify signatures with the given public key
        """
        return PQFEVerifier(
            public_key=public_key,
            variant=self.dilithium_variant
        )
        
    def encrypt_and_sign(self, file_path: str, encryption_public_key: bytes, 
                          signature_private_key: bytes, return_as_data: bool = False) -> Dict[str, Any]:
        """
        Encrypt and sign a file in one operation.
        
        Args:
            file_path (str): Path to the file to encrypt and sign
            encryption_public_key (bytes): Public key for encryption
            signature_private_key (bytes): Private key for signing
            return_as_data (bool): If True, return encrypted content as bytes instead of writing to disk
            
        Returns:
            Dict containing:
            - encrypted_file_path (str) if file written, or encrypted_data (bytes)
            - ciphertext (bytes): The Kyber ciphertext
            - signature (bytes): The Dilithium signature (of the original file)
        """
        # First sign the original file
        signature = self.sign_file(file_path, signature_private_key)
        
        # Then encrypt the file
        encrypt_result = self.encrypt_file(
            file_path=file_path,
            public_key=encryption_public_key,
            return_as_data=return_as_data
        )
        
        # Add the signature to the result
        encrypt_result["signature"] = signature
        
        return encrypt_result
        
    def decrypt_and_verify(self, encrypted_file: str, ciphertext: bytes, signature: bytes,
                            encryption_private_key: bytes, verification_public_key: bytes,
                            return_as_data: bool = False, encrypted_data: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Decrypt a file and verify its signature in one operation.
        
        Args:
            encrypted_file (str): Path to the encrypted file
            ciphertext (bytes): The Kyber ciphertext from encryption
            signature (bytes): The Dilithium signature to verify
            encryption_private_key (bytes): Private key for decryption
            verification_public_key (bytes): Public key for verification
            return_as_data (bool): If True, return decrypted content as bytes instead of writing to disk
            encrypted_data (Optional[bytes]): Directly supplied encrypted data (used for in-memory operations)
            
        Returns:
            Dict containing:
            - decrypted_file_path (str) if file written, or decrypted_data (bytes)
            - verified (bool): True if the signature was verified, False otherwise
        """
        # First decrypt the file
        decrypt_result = self.decrypt_file(
            encrypted_file=encrypted_file,
            ciphertext=ciphertext,
            private_key=encryption_private_key,
            return_as_data=True,  # Always get data for verification
            encrypted_data=encrypted_data
        )
        
        # Get the decrypted data
        decrypted_data = decrypt_result.get("decrypted_data")
        if not decrypted_data:
            raise ValueError("Decryption failed")
        
        # Verify the signature on the decrypted data
        verified = self.verify_data(decrypted_data, signature, verification_public_key)
        
        result = {"verified": verified}
        
        if return_as_data:
            result["decrypted_data"] = decrypted_data
        else:
            # Write the decrypted data to a file
            from .file_ops import write_decrypted_file
            
            if "decrypted_file_path" in decrypt_result:
                # The file was already written
                result["decrypted_file_path"] = decrypt_result["decrypted_file_path"]
            else:
                # We need to write the file
                output_filename = encrypted_file.replace('.enc', '')
                output_dir = "/".join(encrypted_file.split("/")[:-1])
                decrypted_file_path = write_decrypted_file(f"{output_dir}/{output_filename}", decrypted_data)
                result["decrypted_file_path"] = decrypted_file_path
        
        return result