# Copyright (c) 2025 Ernesto Sola-Thomas

"""
Test module for Kyber encryption and decryption functionality.
"""

import unittest
from pathlib import Path
import tempfile
import os

from src.kyber_encryption import KyberEncryption

class TestKyberEncryption(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.encryptor = KyberEncryption()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)
        
    def test_generate_keypair(self):
        """Test key pair generation."""
        public_key, private_key = self.encryptor.generate_keypair()
        self.assertIsNotNone(public_key)
        self.assertIsNotNone(private_key)
        
    def test_encrypt_decrypt_file(self):
        """Test file encryption and decryption."""
        # Create test file
        test_content = b"Test content for encryption"
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_bytes(test_content)
        
        # Generate keys and encrypt
        public_key, private_key = self.encryptor.generate_keypair()
        result = self.encryptor.encrypt_file(str(test_file), public_key)
        
        # Verify encryption result
        self.assertTrue(os.path.exists(result["encrypted_file_path"]))
        self.assertIsNotNone(result["ciphertext"])
        self.assertIsNotNone(result["shared_secret"])
        
        # Decrypt and verify
        decrypted = self.encryptor.decrypt_file(result["encrypted_file_path"], private_key)
        self.assertEqual(decrypted, test_content)
        
if __name__ == '__main__':
    unittest.main() 