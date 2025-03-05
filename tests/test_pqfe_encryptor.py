# Copyright (c) 2025 Ernesto Sola-Thomas

"""
Test subclass for PQFEEncryptor encryption functionality.
"""

import unittest
import os
import tempfile
from pathlib import Path
import base64
import shutil
import sys

# Add parent directory to path to find modules
sys.path.append(str(Path(__file__).parent.parent))
from src.api import PQFE, PQFEEncryptor

class TestPQFEEncryptor(unittest.TestCase):
    """Test cases for the PQFEEncryptor class and related functionality."""

    def setUp(self):
        """Set up test environment before each test."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.test_dir, "test_file.txt")
        self.test_content = b"This is test content for encryption and decryption tests."
        
        # Create a test file
        with open(self.test_file_path, "wb") as f:
            f.write(self.test_content)
        
        # Create a standard PQFE instance and generate keys
        self.pqfe = PQFE(key_directory=self.test_dir)
        self.public_key, self.private_key = self.pqfe.generate_keys()

    def tearDown(self):
        """Clean up after each test."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_pqfe_encryptor_creation(self):
        """Test direct creation of PQFEEncryptor instance."""
        encryptor = PQFEEncryptor(public_key=self.public_key)
        self.assertIsNotNone(encryptor)
        self.assertEqual(encryptor.variant, "Kyber512")  # Default variant

    def test_create_encryptor_factory_method(self):
        """Test the factory method for creating a PQFEEncryptor."""
        encryptor = self.pqfe.create_encryptor(public_key=self.public_key)
        self.assertIsNotNone(encryptor)
        self.assertIsInstance(encryptor, PQFEEncryptor)
        self.assertEqual(encryptor.variant, self.pqfe.encryptor.variant)

    def test_encrypt_data(self):
        """Test encrypting data with PQFEEncryptor."""
        encryptor = self.pqfe.create_encryptor(public_key=self.public_key)
        encrypt_result = encryptor.encrypt_data(self.test_content)
        
        # Verify the result contains the required elements
        self.assertIn("encrypted_data", encrypt_result)
        self.assertIn("ciphertext", encrypt_result)
        self.assertIsInstance(encrypt_result["encrypted_data"], bytes)
        self.assertIsInstance(encrypt_result["ciphertext"], bytes)
        
        # Verify the encrypted data is different from the original
        self.assertNotEqual(encrypt_result["encrypted_data"], self.test_content)

    def test_encrypt_decrypt_cycle(self):
        """Test complete encrypt/decrypt cycle using PQFEEncryptor and PQFE."""
        # Encrypt with PQFEEncryptor (encryption only)
        encryptor = self.pqfe.create_encryptor(public_key=self.public_key)
        encrypt_result = encryptor.encrypt_data(self.test_content)
        
        # Decrypt with main PQFE class
        decrypt_result = self.pqfe.decrypt_data(
            encrypted_data=encrypt_result["encrypted_data"], 
            ciphertext=encrypt_result["ciphertext"],
            private_key=self.private_key
        )
        
        # Verify the decrypted content matches the original
        self.assertIn("decrypted_data", decrypt_result)
        self.assertEqual(decrypt_result["decrypted_data"], self.test_content)

    def test_encrypt_file(self):
        """Test file encryption with PQFEEncryptor."""
        encryptor = self.pqfe.create_encryptor(public_key=self.public_key)
        
        # Test with return_as_data=True
        encrypt_result = encryptor.encrypt_file(
            file_path=self.test_file_path,
            return_as_data=True
        )
        self.assertIn("encrypted_data", encrypt_result)
        self.assertIn("ciphertext", encrypt_result)
        
        # Test writing to file
        output_path = os.path.join(self.test_dir, "encrypted_output.bin")
        encrypt_result = encryptor.encrypt_file(
            file_path=self.test_file_path,
            output_dir=self.test_dir,
            output_filename="encrypted_output.bin"
        )
        self.assertIn("encrypted_file_path", encrypt_result)
        self.assertTrue(os.path.exists(encrypt_result["encrypted_file_path"]))

    def test_different_kyber_variants(self):
        """Test PQFEEncryptor with different Kyber variants."""
        variants = ["Kyber768", "Kyber1024"]
        
        for variant in variants:
            with self.subTest(variant=variant):
                # Create a PQFE instance with the variant
                pqfe = PQFE(variant=variant, key_directory=self.test_dir)
                public_key, private_key = pqfe.generate_keys()
                
                # Create an encryptor and test it
                encryptor = pqfe.create_encryptor(public_key=public_key)
                self.assertEqual(encryptor.variant, variant)
                
                # Test encryption
                encrypt_result = encryptor.encrypt_data(self.test_content)
                self.assertIn("encrypted_data", encrypt_result)
                
                # Test decryption
                decrypt_result = pqfe.decrypt_data(
                    encrypted_data=encrypt_result["encrypted_data"],
                    ciphertext=encrypt_result["ciphertext"],
                    private_key=private_key
                )
                self.assertEqual(decrypt_result["decrypted_data"], self.test_content)

    def test_different_cipher_algorithms(self):
        """Test PQFEEncryptor with different symmetric cipher algorithms."""
        # Test with ChaCha20Poly1305
        pqfe = PQFE(cipher="ChaCha20Poly1305", key_directory=self.test_dir)
        public_key, private_key = pqfe.generate_keys()
        
        encryptor = pqfe.create_encryptor(public_key=public_key)
        encrypt_result = encryptor.encrypt_data(self.test_content)
        
        decrypt_result = pqfe.decrypt_data(
            encrypted_data=encrypt_result["encrypted_data"],
            ciphertext=encrypt_result["ciphertext"],
            private_key=private_key
        )
        
        self.assertEqual(decrypt_result["decrypted_data"], self.test_content)

    def test_invalid_public_key(self):
        """Test behavior with invalid public key."""
        with self.assertRaises(Exception):
            # Create encryptor with invalid key should fail
            encryptor = PQFEEncryptor(public_key=b"invalid_key")
            encryptor.encrypt_data(self.test_content)

    def test_large_data_encryption(self):
        """Test encryption of larger data."""
        large_data = os.urandom(1024 * 1024)  # 1MB of random data
        encryptor = self.pqfe.create_encryptor(public_key=self.public_key)
        encrypt_result = encryptor.encrypt_data(large_data)
        
        decrypt_result = self.pqfe.decrypt_data(
            encrypted_data=encrypt_result["encrypted_data"],
            ciphertext=encrypt_result["ciphertext"],
            private_key=self.private_key
        )
        
        self.assertEqual(decrypt_result["decrypted_data"], large_data)


if __name__ == "__main__":
    unittest.main()
