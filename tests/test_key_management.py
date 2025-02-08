# Copyright (c) 2025 Ernesto Sola-Thomas

"""
Test module for key management functionality.
"""

import unittest
from pathlib import Path
import tempfile
import os

from src import key_management

class TestKeyManagement(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_keys = {
            "public": b"test_public_key_data",
            "private": b"test_private_key_data"
        }
        
    def tearDown(self):
        """Clean up test environment."""
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)
        
    def test_save_load_keys(self):
        """Test saving and loading keys."""
        # Save keys
        public_path, private_path = key_management.save_keys(
            self.test_keys["public"],
            self.test_keys["private"],
            self.test_dir
        )
        
        # Verify files exist
        self.assertTrue(public_path.exists())
        self.assertTrue(private_path.exists())
        
        # Load keys
        loaded_public, loaded_private = key_management.load_keys(self.test_dir)
        
        # Verify loaded keys match original
        self.assertEqual(loaded_public, self.test_keys["public"])
        self.assertEqual(loaded_private, self.test_keys["private"])
        
    def test_generate_key_filename(self):
        """Test key filename generation."""
        filename = key_management.generate_key_filename("public", "Kyber512")
        self.assertIn("public", filename)
        self.assertIn("Kyber512", filename)
        
if __name__ == '__main__':
    unittest.main() 