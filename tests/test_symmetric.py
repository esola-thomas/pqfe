# Copyright (c) 2025 Ernesto Sola-Thomas

"""
Test module for symmetric cipher functionality.
"""

import unittest
import os
import logging
from src.symmetric import get_cipher_instance, AES256GCMCipher, ChaCha20Poly1305Cipher

LOGGING_ENABLED = os.getenv('LOGGING_ENABLED', 'True').lower() == 'true'

if LOGGING_ENABLED:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.CRITICAL)

class TestSymmetricCiphers(unittest.TestCase):
    def setUp(self):
        """Set up test data."""
        self.test_data = b"This is test data for symmetric encryption."
        self.test_key = os.urandom(32)  # Generate a random 32-byte key
        if LOGGING_ENABLED:
            logging.debug("Test environment set up")
    
    def test_aes_gcm_cipher(self):
        """Test AES-256-GCM cipher."""
        cipher = AES256GCMCipher()
        
        # Encrypt data
        encrypted = cipher.encrypt(self.test_data, self.test_key)
        self.assertNotEqual(encrypted, self.test_data)
        if LOGGING_ENABLED:
            logging.debug("Data encrypted with AES-256-GCM")
        
        # Decrypt data
        decrypted = cipher.decrypt(encrypted, self.test_key)
        self.assertEqual(decrypted, self.test_data)
        if LOGGING_ENABLED:
            logging.debug("Data decrypted with AES-256-GCM")
    
    def test_chacha20_poly1305_cipher(self):
        """Test ChaCha20-Poly1305 cipher."""
        cipher = ChaCha20Poly1305Cipher()
        
        # Encrypt data
        encrypted = cipher.encrypt(self.test_data, self.test_key)
        self.assertNotEqual(encrypted, self.test_data)
        if LOGGING_ENABLED:
            logging.debug("Data encrypted with ChaCha20-Poly1305")
        
        # Decrypt data
        decrypted = cipher.decrypt(encrypted, self.test_key)
        self.assertEqual(decrypted, self.test_data)
        if LOGGING_ENABLED:
            logging.debug("Data decrypted with ChaCha20-Poly1305")
    
    def test_cipher_factory(self):
        """Test the cipher factory function."""
        aes_cipher = get_cipher_instance("AES256GCM")
        chacha_cipher = get_cipher_instance("ChaCha20Poly1305")
        
        self.assertIsInstance(aes_cipher, AES256GCMCipher)
        self.assertIsInstance(chacha_cipher, ChaCha20Poly1305Cipher)
        
        # Test with invalid cipher name
        with self.assertRaises(ValueError):
            get_cipher_instance("InvalidCipher")
        
        if LOGGING_ENABLED:
            logging.debug("Cipher factory tests passed")
    
    def test_short_key_handling(self):
        """Test how ciphers handle keys shorter than 32 bytes."""
        short_key = os.urandom(16)  # Only 16 bytes
        
        # Both implementations should raise ValueError
        for cipher_name in ["AES256GCM", "ChaCha20Poly1305"]:
            cipher = get_cipher_instance(cipher_name)
            with self.assertRaises(ValueError):
                cipher.encrypt(self.test_data, short_key)
            
        if LOGGING_ENABLED:
            logging.debug("Short key handling tests passed")

if __name__ == '__main__':
    unittest.main()
