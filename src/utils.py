# utils.py
"""
Utility functions for Post-Quantum File Encryption system.
Provides helper functions used across modules.
"""

from typing import Any, Dict
import json
import base64
from pathlib import Path

def encode_bytes(data: bytes) -> str:
    """
    Encode bytes to a base64 string.
    
    Args:
        data (bytes): Data to encode
        
    Returns:
        str: Base64 encoded string
    """
    return base64.b64encode(data).decode('utf-8')

def decode_bytes(data: str) -> bytes:
    """
    Decode a base64 string to bytes.
    
    Args:
        data (str): Base64 encoded string
        
    Returns:
        bytes: Decoded data
    """
    return base64.b64decode(data.encode('utf-8'))

def create_metadata(
    variant: str,
    file_size: int,
    original_filename: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Create metadata dictionary for encrypted files.
    
    Args:
        variant (str): Kyber variant used
        file_size (int): Original file size
        original_filename (str): Original filename
        **kwargs: Additional metadata
        
    Returns:
        Dict[str, Any]: Metadata dictionary
    """
    metadata = {
        "variant": variant,
        "file_size": file_size,
        "original_filename": original_filename
    }
    metadata.update(kwargs)
    return metadata

def ensure_directory(directory: str) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory (str): Directory path
        
    Returns:
        Path: Path object for directory
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path
