# __init__.py
"""
Post-Quantum File Encryption (PQFE) package.
"""

from .api import PQFE
from .config import KYBER_VARIANTS, DEFAULT_KEY_DIRECTORY, CHUNK_SIZE, MAX_FILE_SIZE, METADATA_VERSION, ENCRYPTION_ALGORITHM
from .file_ops import read_file, write_encrypted_file, read_encrypted_file, write_decrypted_file
from .key_management import save_keys, load_keys
from .kyber_encryption import KyberEncryption
from .symmetric import get_cipher_instance
from .utils import encode_bytes, decode_bytes, create_metadata, ensure_directory
