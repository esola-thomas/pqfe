# Copyright (c) 2025 Ernesto Sola-Thomas

"""
Test module for Kyber encryption functionality.
"""

import unittest
import logging
import os
from src.kyber_encryption import KyberEncryption
from src.file_ops import read_file

# Configure logging
LOGGING_ENABLED = os.getenv('LOGGING_ENABLED', 'True').lower() == 'true'
if LOGGING_ENABLED:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.CRITICAL)

class TestKyberEncryption(unittest.TestCase):
    def setUp(self):
        self.kyber = KyberEncryption(variant="Kyber512", cipher="AES256GCM")
        self.sample_file = 'sample.txt'
        self.encrypted_file = 'sample.txt.enc'
        self.decrypted_file = 'sample_decrypted.txt'
        # Create a sample file
        with open(self.sample_file, 'w') as f:
            f.write('This is a test file.')
        logging.debug('Sample file created.')

    def tearDown(self):
        # Clean up files
        for file_path in [self.sample_file, self.encrypted_file, self.decrypted_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
        logging.debug('Test files cleaned up.')

    def test_generate_keypair(self):
        public_key, private_key = self.kyber.generate_keypair()
        self.assertIsInstance(public_key, bytes)
        self.assertIsInstance(private_key, bytes)
        logging.debug('Key pair generated.')

    def test_encrypt_decrypt_file(self):
        # Generate keypair
        public_key, private_key = self.kyber.generate_keypair()
        
        # Encrypt the file
        result = self.kyber.encrypt_file(self.sample_file, public_key)
        self.assertIn('encrypted_file_path', result)
        self.assertIn('ciphertext', result)
        self.assertIn('shared_secret', result)
        self.assertTrue(os.path.exists(result['encrypted_file_path']))
        logging.debug('File encrypted successfully.')

        # Decrypt the file
        decrypt_result = self.kyber.decrypt_file(
            result['encrypted_file_path'], 
            private_key, 
            result['ciphertext']
        )
        self.assertIn('decrypted_file_path', decrypt_result)
        with open(decrypt_result['decrypted_file_path'], 'rb') as f:
            decrypted_content = f.read()
        
        original_content = read_file(self.sample_file)
        self.assertEqual(decrypted_content, original_content)
        logging.debug('File decrypted successfully.')
    
    def test_encrypt_decrypt_in_memory(self):
        # Generate keypair
        public_key, private_key = self.kyber.generate_keypair()
        
        # Encrypt the file, keeping result in memory
        result = self.kyber.encrypt_file(
            self.sample_file, 
            public_key,
            return_as_data=True
        )
        self.assertIn('encrypted_data', result)
        self.assertIn('ciphertext', result)
        self.assertIn('shared_secret', result)
        logging.debug('File encrypted in memory successfully.')

        # Decrypt the file in memory
        decrypt_result = self.kyber.decrypt_file(
            encrypted_file=self.sample_file,  # This is only used for debugging
            private_key=private_key, 
            ciphertext=result['ciphertext'],
            return_as_data=True
        )
        self.assertIn('decrypted_data', decrypt_result)
        
        original_content = read_file(self.sample_file)
        self.assertEqual(decrypt_result['decrypted_data'], original_content)
        logging.debug('File decrypted in memory successfully.')

    def test_different_ciphers(self):
        """Test both supported symmetric ciphers"""
        for cipher in ["AES256GCM", "ChaCha20Poly1305"]:
            with self.subTest(cipher=cipher):
                kyber = KyberEncryption(variant="Kyber512", cipher=cipher)
                
                # Generate keypair
                public_key, private_key = kyber.generate_keypair()
                
                # Encrypt and decrypt
                result = kyber.encrypt_file(self.sample_file, public_key, return_as_data=True)
                decrypt_result = kyber.decrypt_file(
                    self.sample_file,  # Just for reference
                    private_key, 
                    result['ciphertext'],
                    return_as_data=True
                )
                
                original_content = read_file(self.sample_file)
                self.assertEqual(decrypt_result['decrypted_data'], original_content)
                logging.debug(f'Encryption/decryption with {cipher} successful.')

if __name__ == '__main__':
    unittest.main()