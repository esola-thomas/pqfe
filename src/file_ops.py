# Copyright (c) 2025 Ernesto Sola-Thomas

"""
File operations module for handling file encryption and decryption.
Provides functionality for reading, writing, and processing files.
"""

from typing import BinaryIO, Tuple, Optional
from pathlib import Path
import os
import json

def read_file(file_path: str) -> bytes:
    """
    Read file contents as bytes.
    
    Args:
        file_path (str): Path to the file to read
        
    Returns:
        bytes: File contents
        
    Raises:
        FileNotFoundError: If the file does not exist
        IOError: If there is an error reading the file
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    try:
        # read_bytes handles both binary and text files
        return path.read_bytes()
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {str(e)}")

def write_encrypted_file(
    file_path: str,
    encrypted_content: bytes,
    ciphertext: bytes,
    metadata: dict
) -> str:
    """
    Write encrypted content to file with metadata.
    
    Args:
        file_path (str): Original file path
        encrypted_content (bytes): Encrypted file content
        ciphertext (bytes): Encryption ciphertext
        metadata (dict): Additional metadata to store
        
    Returns:
        str: Path to the encrypted file
    """
    encrypted_file_path = f"{file_path}.enc"
    with open(encrypted_file_path, 'wb') as f:
        f.write(encrypted_content)
        # Assuming metadata and ciphertext are stored in a JSON format
        f.write(b'\n')  # Newline to separate content and metadata
        f.write(json.dumps({'ciphertext': ciphertext.hex(), 'metadata': metadata}).encode())
    return encrypted_file_path

def read_encrypted_file(encrypted_file: str) -> Tuple[bytes, bytes, dict]:
    """
    Read encrypted file and extract content, ciphertext, and metadata.
    
    Args:
        encrypted_file (str): Path to encrypted file
        
    Returns:
        Tuple[bytes, bytes, dict]: (encrypted_content, ciphertext, metadata)
    """
    with open(encrypted_file, 'rb') as f:
        content = f.read()
        encrypted_content, metadata_json = content.split(b'\n', 1)
        metadata = json.loads(metadata_json)
        ciphertext = bytes.fromhex(metadata['ciphertext'])
    return encrypted_content, ciphertext, metadata['metadata']

def write_decrypted_file(
    encrypted_file: str,
    decrypted_content: bytes,
    output_path: Optional[str] = None
) -> str:
    """
    Write decrypted content to file.
    
    Args:
        encrypted_file (str): Original encrypted file path
        decrypted_content (bytes): Decrypted content
        output_path (Optional[str]): Custom output path
        
    Returns:
        str: Path to the decrypted file
    """
    if output_path is None:
        output_path = encrypted_file.replace('.enc', '')
    with open(output_path, 'wb') as f:
        f.write(decrypted_content)
    return output_path 