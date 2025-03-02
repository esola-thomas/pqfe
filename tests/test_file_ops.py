# Copyright (c) 2025 Ernesto Sola-Thomas

"""
Test module for file operations functionality.
"""

import unittest
from pathlib import Path
import tempfile
import os
import logging

from src import file_ops

LOGGING_ENABLED = os.getenv('LOGGING_ENABLED', 'True').lower() == 'true'

if LOGGING_ENABLED:
    logging.basicConfig(level=logging.DEBUG)

class TestFileOperations(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_content = b"Test content for file operations"
        self.test_file = Path(self.test_dir) / "test.txt"
        self.test_file.write_bytes(self.test_content)
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
        
    def test_read_file(self):
        """Test reading file contents."""
        content = file_ops.read_file(str(self.test_file))
        self.assertEqual(content, self.test_content)
        if LOGGING_ENABLED:
            logging.debug("File read successfully")
        
    def test_write_read_encrypted_file(self):
        """Test writing and reading encrypted file."""
        # Test data
        encrypted_content = b"encrypted_content"
        
        # Define custom output path
        encrypted_path = str(Path(self.test_dir) / "encrypted.bin")
        
        # Write encrypted file
        result_path = file_ops.write_encrypted_file(
            encrypted_path,
            encrypted_content
        )
        if LOGGING_ENABLED:
            logging.debug(f"Encrypted file written to {result_path}")
        
        # Verify file exists
        self.assertTrue(os.path.exists(result_path))
        
        # Read encrypted file
        read_encrypted_content = file_ops.read_encrypted_file(result_path)
        if LOGGING_ENABLED:
            logging.debug("Encrypted file read successfully")
        
        # Verify contents
        self.assertEqual(read_encrypted_content, encrypted_content)
    
    def test_write_read_decrypted_file(self):
        """Test writing and reading decrypted file."""
        # Test data
        decrypted_content = b"decrypted_content"
        
        # Define custom output path 
        decrypted_path = str(Path(self.test_dir) / "decrypted.txt")
        
        # Write decrypted file
        result_path = file_ops.write_decrypted_file(
            decrypted_path,
            decrypted_content
        )
        if LOGGING_ENABLED:
            logging.debug(f"Decrypted file written to {result_path}")
        
        # Verify file exists
        self.assertTrue(os.path.exists(result_path))
        
        # Read file
        with open(result_path, 'rb') as f:
            read_content = f.read()
        
        # Verify contents
        self.assertEqual(read_content, decrypted_content)
        
if __name__ == '__main__':
    unittest.main()