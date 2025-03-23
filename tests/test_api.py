# Copyright (c) 2025 Ernesto Sola-Thomas
"""
Test module for API functionality.
"""

import unittest
from pathlib import Path
import tempfile
import os
import logging
from src.api import PQFE

LOGGING_ENABLED = os.getenv('LOGGING_ENABLED', 'True').lower() == 'true'

if LOGGING_ENABLED:
    logging.basicConfig(level=logging.DEBUG)

class TestPQFE(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = tempfile.mkdtemp()
        
        # Configure PQFE instance with test directory for keys
        self.key_dir = Path(self.test_dir) / "keys"
        self.key_dir.mkdir(exist_ok=True)
        self.pqfe = PQFE(
            variant="Kyber512", 
            key_directory=str(self.key_dir),
            cipher="AES256GCM"
        )
        
        # Create a test file
        self.test_file = Path(self.test_dir) / "test.txt"
        self.test_content = "This is a test file."
        self.test_file.write_text(self.test_content)
        
        if LOGGING_ENABLED:
            logging.debug(f"Test environment set up with directory: {self.test_dir}")
            logging.debug(f"Output directory set up: {self.output_dir}")
            logging.debug(f"Test file created at: {self.test_file}")

    def tearDown(self):
        """Clean up test environment."""
        for directory in [self.test_dir, self.output_dir]:
            for root, dirs, files in os.walk(directory, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(directory)
        if LOGGING_ENABLED:
            logging.debug(f"Test environment cleaned up")

    def test_generate_and_load_keys(self):
        """Test key generation and loading."""
        public_key, private_key = self.pqfe.generate_keys()
        if LOGGING_ENABLED:
            logging.debug("Keys generated successfully")
            
        loaded_public_key, loaded_private_key = self.pqfe.load_keys()
        if LOGGING_ENABLED:
            logging.debug("Keys loaded successfully")
            
        self.assertEqual(public_key, loaded_public_key)
        self.assertEqual(private_key, loaded_private_key)

    def test_encrypt_and_decrypt_file(self):
        """Test file encryption and decryption."""
        public_key, private_key = self.pqfe.generate_keys()
        if LOGGING_ENABLED:
            logging.debug("Generated keys for encryption test")
            
        # Encrypt file with custom output location
        encrypt_result = self.pqfe.encrypt_file(
            str(self.test_file), 
            public_key,
            output_dir=self.output_dir,
            output_filename="encrypted.bin"
        )
        
        self.assertIn('encrypted_file_path', encrypt_result)
        encrypted_path = encrypt_result['encrypted_file_path']
        self.assertTrue(os.path.exists(encrypted_path))
        if LOGGING_ENABLED:
            logging.debug(f"File encrypted to: {encrypted_path}")

        # Decrypt file with custom output location
        decrypt_result = self.pqfe.decrypt_file(
            encrypted_path,
            encrypt_result['ciphertext'],
            private_key,
            output_dir=self.output_dir,
            output_filename="decrypted.txt"
        )
        
        self.assertIn('decrypted_file_path', decrypt_result)
        decrypted_path = decrypt_result['decrypted_file_path']
        self.assertTrue(os.path.exists(decrypted_path))
        if LOGGING_ENABLED:
            logging.debug(f"File decrypted to: {decrypted_path}")
            
        # Verify content
        with open(decrypted_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, self.test_content)
        if LOGGING_ENABLED:
            logging.debug("Decrypted content verified")

    def test_in_memory_operations(self):
        """Test in-memory encryption and decryption."""
        public_key, private_key = self.pqfe.generate_keys()

        # Encrypt file, return data in memory
        encrypt_result = self.pqfe.encrypt_file(
            str(self.test_file), 
            public_key,
            return_as_data=True
        )

        self.assertIn('encrypted_data', encrypt_result)
        self.assertIn('ciphertext', encrypt_result)
        if LOGGING_ENABLED:
            logging.debug("File encrypted in memory")

        # Decrypt data in memory – pass encrypted_data explicitly!
        decrypt_result = self.pqfe.decrypt_file(
            str(self.test_file),  # This path is not used when encrypted_data is provided
            encrypt_result['ciphertext'],
            private_key,
            return_as_data=True,
            encrypted_data=encrypt_result['encrypted_data']
        )

        self.assertIn('decrypted_data', decrypt_result)
        decrypted_content = decrypt_result['decrypted_data']
        self.assertEqual(decrypted_content.decode('utf-8'), self.test_content)
        if LOGGING_ENABLED:
            logging.debug("In-memory decrypted content verified")
    
    def test_different_ciphers(self):
        """Test different symmetric cipher options."""
        for cipher in ["AES256GCM", "ChaCha20Poly1305"]:
            with self.subTest(cipher=cipher):
                pqfe = PQFE(
                    variant="Kyber512", 
                    key_directory=str(self.key_dir),
                    cipher=cipher
                )

                public_key, private_key = pqfe.generate_keys()

                # Test with this cipher (in-memory)
                encrypt_result = pqfe.encrypt_file(
                    str(self.test_file),
                    public_key,
                    return_as_data=True
                )

                decrypt_result = pqfe.decrypt_file(
                    str(self.test_file),
                    encrypt_result['ciphertext'],
                    private_key,
                    return_as_data=True,
                    encrypted_data=encrypt_result['encrypted_data']
                )

                self.assertEqual(decrypt_result['decrypted_data'].decode('utf-8'), self.test_content)
                if LOGGING_ENABLED:
                    logging.debug(f"Encryption/decryption with {cipher} successful")

    def test_pqfe_signer(self):
        """Test PQFESigner functionality."""
        public_key, private_key = self.pqfe.generate_signature_keys()
        signer = self.pqfe.create_signer(private_key)
        
        data = b"Test data for signing"
        signature = signer.sign_data(data)
        
        verifier = self.pqfe.create_verifier(public_key)
        self.assertTrue(verifier.verify_data(data, signature))

    def test_pqfe_verifier(self):
        """Test PQFEVerifier functionality."""
        public_key, private_key = self.pqfe.generate_signature_keys()
        verifier = self.pqfe.create_verifier(public_key)
        
        data = b"Test data for verification"
        signer = self.pqfe.create_signer(private_key)
        signature = signer.sign_data(data)
        
        self.assertTrue(verifier.verify_data(data, signature))

    def test_encrypt_and_sign(self):
        """Test encrypt_and_sign functionality."""
        encryption_public_key, encryption_private_key = self.pqfe.generate_keys()
        signature_public_key, signature_private_key = self.pqfe.generate_signature_keys()
        
        result = self.pqfe.encrypt_and_sign(
            file_path=str(self.test_file),
            encryption_public_key=encryption_public_key,
            signature_private_key=signature_private_key,
            return_as_data=True
        )
        
        self.assertIn('encrypted_data', result)
        self.assertIn('ciphertext', result)
        self.assertIn('signature', result)

    def test_decrypt_and_verify(self):
        """Test decrypt_and_verify functionality."""
        encryption_public_key, encryption_private_key = self.pqfe.generate_keys()
        signature_public_key, signature_private_key = self.pqfe.generate_signature_keys()
        
        encrypt_result = self.pqfe.encrypt_and_sign(
            file_path=str(self.test_file),
            encryption_public_key=encryption_public_key,
            signature_private_key=signature_private_key,
            return_as_data=True
        )
        
        decrypt_result = self.pqfe.decrypt_and_verify(
            encrypted_file=str(self.test_file),
            ciphertext=encrypt_result['ciphertext'],
            signature=encrypt_result['signature'],
            encryption_private_key=encryption_private_key,
            verification_public_key=signature_public_key,
            return_as_data=True,
            encrypted_data=encrypt_result['encrypted_data']
        )
        
        self.assertIn('decrypted_data', decrypt_result)
        self.assertTrue(decrypt_result['verified'])

if __name__ == '__main__':
    unittest.main()