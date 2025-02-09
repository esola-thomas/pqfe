# Copyright (c) 2025 Ernesto Sola-Thomas

"""
Test module for Kyber encryption and decryption functionality.
"""

import unittest
from pathlib import Path
import tempfile
import os
import logging

from src.kyber_encryption import KyberEncryption

LOGGING_ENABLED = os.getenv('LOGGING_ENABLED', 'True').lower() == 'true'

if LOGGING_ENABLED:
    logging.basicConfig(level=logging.DEBUG)

class TestKyberEncryption(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.encryptor = KyberEncryption()
        self.test_dir = tempfile.mkdtemp()
        if LOGGING_ENABLED:
            logging.debug(f"Test environment set up with directory: {self.test_dir}")
        
    def tearDown(self):
        """Clean up test environment."""
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)
        if LOGGING_ENABLED:
            logging.debug(f"Test environment cleaned up for directory: {self.test_dir}")
        
    def test_generate_keypair(self):
        """Test key pair generation."""
        public_key, private_key = self.encryptor.generate_keypair()
        self.assertIsNotNone(public_key)
        self.assertIsNotNone(private_key)
        if LOGGING_ENABLED:
            logging.debug("Key pair generated successfully")
        
    def test_encrypt_decrypt_file(self):
        """Test file encryption and decryption."""
        # Create test file
        test_content = b"Test content for encryption"
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_bytes(test_content)
        if LOGGING_ENABLED:
            logging.debug(f"Test file created at: {test_file}")
        
        # Generate keys and encrypt
        public_key, private_key = self.encryptor.generate_keypair()
        result = self.encryptor.encrypt_file(str(test_file), public_key)
        if LOGGING_ENABLED:
            logging.debug(f"File encrypted to: {result['encrypted_file_path']}")
        
        # Verify encryption result
        self.assertTrue(os.path.exists(result["encrypted_file_path"]))
        self.assertIsNotNone(result["ciphertext"])
        self.assertIsNotNone(result["shared_secret"])
        if LOGGING_ENABLED:
            logging.debug("Encryption result verified")
        
        # Decrypt and verify
        decrypted = self.encryptor.decrypt_file(result["encrypted_file_path"], private_key)
        self.assertEqual(decrypted, test_content)
        if LOGGING_ENABLED:
            logging.debug("File decrypted and content verified")
        
if __name__ == '__main__':
    unittest.main() 