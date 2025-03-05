# Copyright (c) 2025 Ernesto Sola-Thomas

"""
Test elabroated cases for distributing encrypted files.
"""


import unittest
import os
import tempfile
import shutil

from external.pqfe.src.api import PQFE

class TestApiIntegration(unittest.TestCase):
    """Integration tests for PQFE API functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_file.txt")
        with open(self.test_file, 'wb') as f:
            f.write(b"This is test data for integration testing.")

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_storage_to_requestor_flow(self):
        """
        Test the storage-to-requestor flow:
        1. Storage has a file encrypted with root key
        2. Storage decrypts with root key
        3. Storage re-encrypts with requestor's public key using PQFEEncryptor
        4. Requestor decrypts with their own private key
        """
        # Create two PQFE instances - one for storage and one for requestor
        storage_pqfe = PQFE()
        requestor_pqfe = PQFE()
        
        # Generate keys for both parties
        root_public, root_private = storage_pqfe.generate_keys()
        requestor_public, requestor_private = requestor_pqfe.generate_keys()
        
        # Step 1: Encrypt a file with root key (simulating initial storage)
        with open(self.test_file, 'rb') as f:
            original_content = f.read()
        
        encrypt_result = storage_pqfe.encrypt_data(
            data=original_content,
            public_key=root_public
        )
        
        # Step 2: Storage decrypts the file with root private key
        decrypt_result = storage_pqfe.decrypt_data(
            encrypted_data=encrypt_result['encrypted_data'],
            ciphertext=encrypt_result['ciphertext'],
            private_key=root_private
        )
        plaintext = decrypt_result['decrypted_data']
        
        # Step 3: Storage re-encrypts for requestor using PQFEEncryptor
        encryptor = storage_pqfe.create_encryptor(public_key=requestor_public)
        requestor_encrypt_result = encryptor.encrypt_data(plaintext)
        
        # Step 4: Requestor decrypts with their private key
        requestor_decrypt_result = requestor_pqfe.decrypt_data(
            encrypted_data=requestor_encrypt_result['encrypted_data'],
            ciphertext=requestor_encrypt_result['ciphertext'],
            private_key=requestor_private
        )
        
        # Verify the content is preserved through the entire flow
        self.assertEqual(requestor_decrypt_result['decrypted_data'], original_content)

    def test_multi_requestor_scenario(self):
        """
        Test scenario with multiple requestors:
        1. Storage has a file encrypted with root key
        2. Storage shares with multiple requestors by re-encrypting for each
        """
        # Setup storage
        storage_pqfe = PQFE()
        root_public, root_private = storage_pqfe.generate_keys()
        
        # Setup 3 different requestors
        requestor_instances = []
        for i in range(3):
            pqfe = PQFE()
            public, private = pqfe.generate_keys()
            requestor_instances.append({
                'pqfe': pqfe,
                'public': public,
                'private': private
            })
        
        # Encrypt original content with root key
        with open(self.test_file, 'rb') as f:
            original_content = f.read()
            
        encrypt_result = storage_pqfe.encrypt_data(
            data=original_content,
            public_key=root_public
        )
        
        # Decrypt with root key
        decrypt_result = storage_pqfe.decrypt_data(
            encrypted_data=encrypt_result['encrypted_data'],
            ciphertext=encrypt_result['ciphertext'],
            private_key=root_private
        )
        plaintext = decrypt_result['decrypted_data']
        
        # Re-encrypt for each requestor and verify they can decrypt
        for requestor in requestor_instances:
            # Create an encryptor for this requestor
            encryptor = storage_pqfe.create_encryptor(public_key=requestor['public'])
            req_encrypt_result = encryptor.encrypt_data(plaintext)
            
            # Requestor decrypts
            req_decrypt_result = requestor['pqfe'].decrypt_data(
                encrypted_data=req_encrypt_result['encrypted_data'],
                ciphertext=req_encrypt_result['ciphertext'],
                private_key=requestor['private']
            )
            
            # Verify content
            self.assertEqual(req_decrypt_result['decrypted_data'], original_content)


if __name__ == "__main__":
    unittest.main()
