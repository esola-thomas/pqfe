# Copyright (c) 2025 Ernesto Sola-Thomas

"""
Key management module for handling Kyber key operations.
Provides functionality for key generation, storage, and loading.
"""

from typing import Tuple, Optional
from pathlib import Path
import json
import base64
import oqs 

def save_keys(public_key: bytes, private_key: bytes, directory: str, 
              pub_filename: str = "key.pub.bin", priv_filename: str = "key.bin") -> Tuple[Path, Path]:
    """
    Save public and private keys to files.
    
    Args:
        public_key (bytes): Public key to save
        private_key (bytes): Private key to save
        directory (str): Directory to save keys in
        pub_filename (str, optional): Filename for public key. Defaults to "key.pub.bin"
        priv_filename (str, optional): Filename for private key. Defaults to "key.bin"
        
    Returns:
        Tuple[Path, Path]: Paths to saved public and private key files
    """
    # Create directory if it doesn't exist
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create paths for key files
    pub_path = dir_path / pub_filename
    priv_path = dir_path / priv_filename
    
    # Write keys to files
    pub_path.write_bytes(public_key)
    priv_path.write_bytes(private_key)
    
    return pub_path, priv_path

def load_keys(directory: str, pub_filename: str = "key.pub.bin", priv_filename: str = "key.bin") -> Tuple[Optional[bytes], Optional[bytes]]:
    """
    Load public and private keys from files.
    
    Args:
        directory (str): Directory containing key files
        
    Returns:
        Tuple[Optional[bytes], Optional[bytes]]: Loaded public and private keys
    """
    dir_path = Path(directory)
    pub_path = dir_path / pub_filename
    priv_path = dir_path / priv_filename
    
    # Check if both key files exist
    if not pub_path.exists() or not priv_path.exists():
        return None, None
        
    try:
        # Read keys from files
        public_key = pub_path.read_bytes()
        private_key = priv_path.read_bytes()
        return public_key, private_key
    except Exception as e:
        print(f"Error loading keys: {str(e)}")
        return None, None