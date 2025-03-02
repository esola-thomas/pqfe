# Copyright (c) 2025 Ernesto Sola-Thomas
"""
File operations module for handling file encryption and decryption.
Provides functionality for reading, writing, and processing files.
"""

from pathlib import Path

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
        return path.read_bytes()
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {str(e)}")

def write_encrypted_file(file_path: str, encrypted_content: bytes) -> str:
    """
    Write encrypted content to file.
    
    Args:
        file_path (str): Full path for the encrypted file
        encrypted_content (bytes): Encrypted file content
        
    Returns:
        str: Path to the encrypted file
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(encrypted_content)
    return str(path)

def read_encrypted_file(encrypted_file: str) -> bytes:
    """
    Read encrypted file content.
    
    Args:
        encrypted_file (str): Path to encrypted file
        
    Returns:
        bytes: Encrypted content
    """
    with open(encrypted_file, 'rb') as f:
        return f.read()

def write_decrypted_file(file_path: str, decrypted_content: bytes) -> str:
    """
    Write decrypted content to file.
    
    Args:
        file_path (str): Full path for the decrypted file
        decrypted_content (bytes): Decrypted file content
        
    Returns:
        str: Path to the decrypted file
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(decrypted_content)
    return str(path)
