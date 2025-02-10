# Copyright (c) 2025 Ernesto Sola-Thomas

"""
Test module for Kyber encryption functionality.
"""

import unittest
import logging
import os
from src.kyber_encryption import KyberEncryption
from src.file_ops import read_file, write_decrypted_file

# Configure logging
LOGGING_ENABLED = os.getenv('LOGGING_ENABLED', 'True').lower() == 'true'
if LOGGING_ENABLED:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.CRITICAL)

class TestKyberEncryption(unittest.TestCase):
    def setUp(self):
        self.kyber = KyberEncryption()
        self.sample_file = 'sample.txt'
        self.encrypted_file = 'sample.txt.enc'
        self.decrypted_file = 'sample_decrypted.txt'
        # Create a sample file
        with open(self.sample_file, 'w') as f:
            f.write('This is a test file.')
        logging.debug('Sample file created.')

    def tearDown(self):
        # Clean up files
        if os.path.exists(self.sample_file):
            os.remove(self.sample_file)
        if os.path.exists(self.encrypted_file):
            os.remove(self.encrypted_file)
        if os.path.exists(self.decrypted_file):
            os.remove(self.decrypted_file)
        logging.debug('Test files cleaned up.')

    def test_generate_keypair(self):
        public_key, private_key = self.kyber.generate_keypair()
        self.assertIsInstance(public_key, bytes)
        self.assertIsInstance(private_key, bytes)
        logging.debug('Key pair generated.')

    def test_encrypt_file(self):
        public_key, _ = self.kyber.generate_keypair()
        result = self.kyber.encrypt_file(self.sample_file, public_key)
        self.assertIn('encrypted_file_path', result)
        self.assertIn('ciphertext', result)
        self.assertIn('shared_secret', result)
        self.assertTrue(os.path.exists(result['encrypted_file_path']))
        logging.debug('File encrypted successfully.')

    def test_decrypt_file(self):
        public_key, private_key = self.kyber.generate_keypair()
        self.kyber.encrypt_file(self.sample_file, public_key)
        decrypted_content = self.kyber.decrypt_file(self.encrypted_file, private_key)
        original_content = read_file(self.sample_file)
        self.assertEqual(decrypted_content, original_content)
        logging.debug('File decrypted successfully.')

if __name__ == '__main__':
    unittest.main() 