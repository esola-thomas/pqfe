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
        ciphertext = b"ciphertext"
        metadata = {"version": "1.0", "algorithm": "test"}
        
        # Write encrypted file
        encrypted_path = file_ops.write_encrypted_file(
            str(self.test_file),
            encrypted_content
        )
        if LOGGING_ENABLED:
            logging.debug(f"Encrypted file written to {encrypted_path}")
        
        # Verify file exists
        self.assertTrue(os.path.exists(encrypted_path))
        
        # Read encrypted file
        read_encripted_content = file_ops.read_encrypted_file(encrypted_path)
        if LOGGING_ENABLED:
            logging.debug("Encrypted file read successfully")
        
        # Verify contents
        self.assertEqual(read_encripted_content, encrypted_content)
        
if __name__ == '__main__':
    unittest.main() 