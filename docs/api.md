# API Documentation

## PQFE Class

The main interface for Post-Quantum File Encryption operations.

### Initialization

```python
from pqfe import PQFE

# Initialize with default settings (Kyber512)
pqfe = PQFE()

# Initialize with specific variant
pqfe = PQFE(variant="Kyber768")

# Initialize with custom key directory
pqfe = PQFE(key_directory="/path/to/keys")
```

### Key Management

#### generate_keys()
Generate a new public/private key pair.

```python
public_key, private_key = pqfe.generate_keys()
```

Returns:
- `public_key` (bytes): Public key for encryption
- `private_key` (bytes): Private key for decryption

#### load_keys()
Load existing keys from the configured directory.

```python
public_key, private_key = pqfe.load_keys()
```

Returns:
- `public_key` (Optional[bytes]): Loaded public key or None if not found
- `private_key` (Optional[bytes]): Loaded private key or None if not found

### File Operations

#### encrypt_file(file_path: str, public_key: Optional[bytes] = None)
Encrypt a file using Kyber.

```python
result = pqfe.encrypt_file("document.txt", public_key)
```

Parameters:
- `file_path` (str): Path to the file to encrypt
- `public_key` (Optional[bytes]): Public key for encryption. If None, loads from key directory.

Returns:
- Dictionary containing:
  - `encrypted_file_path` (str): Path to the encrypted file
  - `ciphertext` (bytes): Kyber ciphertext
  - `shared_secret` (bytes): Shared secret used for encryption

#### decrypt_file(encrypted_file: str, private_key: Optional[bytes] = None)
Decrypt an encrypted file.

```python
decrypted_path = pqfe.decrypt_file("document.txt.encrypted", private_key)
```

Parameters:
- `encrypted_file` (str): Path to the encrypted file
- `private_key` (Optional[bytes]): Private key for decryption. If None, loads from key directory.

Returns:
- `str`: Path to the decrypted file

## Supported Kyber Variants

- `Kyber512`: 128-bit classical / 64-bit quantum security
- `Kyber768`: 192-bit classical / 96-bit quantum security
- `Kyber1024`: 256-bit classical / 128-bit quantum security

## Error Handling

The API may raise the following exceptions:

- `ValueError`: Invalid parameters or configuration
- `FileNotFoundError`: File or key not found
- `EncryptionError`: Encryption operation failed
- `DecryptionError`: Decryption operation failed
- `KeyError`: Key management operation failed

Example error handling:

```python
try:
    result = pqfe.encrypt_file("document.txt")
except FileNotFoundError:
    print("File not found")
except EncryptionError as e:
    print(f"Encryption failed: {e}") 