# config.py
"""
Configuration module for Post-Quantum File Encryption system.
Defines constants and configuration options.
"""

from pathlib import Path

# Kyber variant configurations
KYBER_VARIANTS = {
    "Kyber512": {
        "name": "Kyber512",
        "security_level": 1,
        "nist_level": 1,
        "description": "128-bit classical / 64-bit quantum security"
    },
    "Kyber768": {
        "name": "Kyber768",
        "security_level": 3,
        "nist_level": 3,
        "description": "192-bit classical / 96-bit quantum security"
    },
    "Kyber1024": {
        "name": "Kyber1024",
        "security_level": 5,
        "nist_level": 5,
        "description": "256-bit classical / 128-bit quantum security"
    }
}

# Default paths
DEFAULT_KEY_DIRECTORY = str(Path.home() / ".pqfe" / "keys")

# File operation settings
CHUNK_SIZE = 1024 * 1024  # 1MB chunks for file operations
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB maximum file size

# Encryption settings
METADATA_VERSION = "1.0"
ENCRYPTION_ALGORITHM = "AES-256-GCM"  # For hybrid encryption 
