# Copyright (c) 2025 Ernesto Sola-Thomas
"""
Key management module for the PQFE system.
Handles key generation, storage, and retrieval.
"""
from typing import Tuple, Optional
import os
from pathlib import Path

def save_keys(public_key: bytes, private_key: bytes, key_directory: str, key_type: str = "encryption") -> None:
    """
    Save public and private keys to the specified directory.
    
    Args:
        public_key (bytes): Public key to save
        private_key (bytes): Private key to save
        key_directory (str): Directory to save keys to
        key_type (str): Type of key to save (encryption or signature)
        
    Returns:
        None
    """
    directory = Path(key_directory)
    directory.mkdir(parents=True, exist_ok=True)
    
    # Use type-specific filenames
    if key_type == "signature":
        pub_key_path = directory / "signature_public_key.bin"
        priv_key_path = directory / "signature_private_key.bin"
    else:
        # Default to encryption keys
        pub_key_path = directory / "encryption_public_key.bin"
        priv_key_path = directory / "encryption_private_key.bin"
    
    with open(pub_key_path, 'wb') as f:
        f.write(public_key)
    
    # Set restricted permissions for private key
    with open(priv_key_path, 'wb') as f:
        f.write(private_key)
    
    try:
        os.chmod(priv_key_path, 0o600)  # Only owner can read/write
    except Exception:
        # On some systems or file systems, chmod might not work
        pass

def load_keys(key_directory: str, key_type: str = "encryption") -> Tuple[Optional[bytes], Optional[bytes]]:
    """
    Load public and private keys from the specified directory.
    
    Args:
        key_directory (str): Directory to load keys from
        key_type (str): Type of key to load (encryption or signature)
        
    Returns:
        Tuple[Optional[bytes], Optional[bytes]]: (public_key, private_key), or (None, None) if keys don't exist
    """
    directory = Path(key_directory)
    
    # Use type-specific filenames
    if key_type == "signature":
        pub_key_path = directory / "signature_public_key.bin"
        priv_key_path = directory / "signature_private_key.bin"
    else:
        # Default to encryption keys
        pub_key_path = directory / "encryption_public_key.bin"
        priv_key_path = directory / "encryption_private_key.bin"
    
    if not pub_key_path.exists() or not priv_key_path.exists():
        return None, None
    
    with open(pub_key_path, 'rb') as f:
        public_key = f.read()
    
    with open(priv_key_path, 'rb') as f:
        private_key = f.read()
    
    return public_key, private_key

def delete_keys(key_directory: str, key_type: str = "encryption") -> bool:
    """
    Delete keys from the specified directory.
    
    Args:
        key_directory (str): Directory containing keys to delete
        key_type (str): Type of key to delete (encryption or signature)
        
    Returns:
        bool: True if keys were deleted, False if keys didn't exist
    """
    directory = Path(key_directory)
    
    # Use type-specific filenames
    if key_type == "signature":
        pub_key_path = directory / "signature_public_key.bin"
        priv_key_path = directory / "signature_private_key.bin"
    else:
        # Default to encryption keys
        pub_key_path = directory / "encryption_public_key.bin"
        priv_key_path = directory / "encryption_private_key.bin"
    
    deleted = False
    
    if pub_key_path.exists():
        pub_key_path.unlink()
        deleted = True
    
    if priv_key_path.exists():
        priv_key_path.unlink()
        deleted = True
    
    return deleted
