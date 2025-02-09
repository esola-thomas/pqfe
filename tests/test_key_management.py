# Copyright (c) 2025 Ernesto Sola-Thomas

"""
Test module for key management functionality.
"""

import unittest
import tempfile
import os
import logging

from src import key_management

LOGGING_ENABLED = True  # Set this to False to disable logging

if LOGGING_ENABLED:
    logging.basicConfig(level=logging.DEBUG)

class TestKeyManagement(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_keys = {
            "public": b"test_public_key_data",
            "private": b"test_private_key_data"
        }
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
        
    def test_save_load_keys(self):
        """Test saving and loading keys."""
        # Save keys
        public_path, private_path = key_management.save_keys(
            self.test_keys["public"],
            self.test_keys["private"],
            self.test_dir
        )
        if LOGGING_ENABLED:
            logging.debug(f"Keys saved to {public_path} and {private_path}")
        
        # Verify files exist
        self.assertTrue(public_path.exists())
        self.assertTrue(private_path.exists())
        
        # Load keys
        loaded_public, loaded_private = key_management.load_keys(self.test_dir)
        if LOGGING_ENABLED:
            logging.debug("Keys loaded successfully")
        
        # Verify loaded keys match original
        self.assertEqual(loaded_public, self.test_keys["public"])
        self.assertEqual(loaded_private, self.test_keys["private"])
        
if __name__ == '__main__':
    unittest.main() 