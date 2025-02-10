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
        self.pqfe = PQFE()
        self.test_dir = tempfile.mkdtemp()
        self.test_file = Path(self.test_dir) / "test.txt"
        self.encrypted_file = Path(self.test_dir) / "test.txt.enc"
        self.decrypted_file = Path(self.test_dir) / "test_decrypted.txt"
        # Create a test file
        self.test_file.write_text('This is a test file.')
        if LOGGING_ENABLED:
            logging.debug(f"Test environment set up with directory: {self.test_dir}")
            logging.debug(f"Test file created at: {self.test_file}")

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
            
        encrypt_result = self.pqfe.encrypt_file(str(self.test_file), public_key)
        self.assertIn('encrypted_file_path', encrypt_result)
        self.assertTrue(Path(encrypt_result['encrypted_file_path']).exists())
        if LOGGING_ENABLED:
            logging.debug(f"File encrypted to: {encrypt_result['encrypted_file_path']}")

        decrypted_path = self.pqfe.decrypt_file(encrypt_result['encrypted_file_path'], encrypt_result['ciphertext'], private_key, str(self.decrypted_file))
        self.assertTrue(Path(decrypted_path).exists())
        if LOGGING_ENABLED:
            logging.debug(f"File decrypted to: {decrypted_path}")
            
        content = Path(decrypted_path).read_text()
        self.assertEqual(content, 'This is a test file.')
        if LOGGING_ENABLED:
            logging.debug("Decrypted content verified")

if __name__ == '__main__':
    unittest.main()