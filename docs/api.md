# API Documentation

## PQFE Class

The main interface for Post-Quantum File Encryption operations. This API supports:
- Multiple Kyber variants (Kyber512, Kyber768, Kyber1024)
- A pluggable symmetric cipher layer (default: AES256GCM, with ChaCha20Poly1305 as an alternative)
- Configurable file I/O (choose output directory, filename, or return data directly)
- Integrated key management using secure file storage

### Initialization

```python
from pqfe import PQFE

# Initialize with default settings (Kyber512, AES256GCM)
pqfe = PQFE()

# Initialize with a specific Kyber variant and symmetric cipher
pqfe = PQFE(variant="Kyber768", cipher="ChaCha20Poly1305")

# Initialize with a custom key directory
pqfe = PQFE(key_directory="/path/to/keys")
```

### Key Management

#### generate_keys()
Generate a new public/private key pair and save them to the configured key directory.

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

#### encrypt_file(file_path: str, public_key: Optional[bytes] = None, output_dir: Optional[str] = None, output_filename: Optional[str] = None, return_as_data: bool = False)
Encrypt a file using Kyber for key encapsulation and a symmetric cipher (default AES256GCM, configurable).

```python
result = pqfe.encrypt_file("document.txt", public_key=public_key)
```

Parameters:
- `file_path` (str): Path to the file to encrypt.
- `public_key` (Optional[bytes]): Public key for encryption. If not provided, users should load or supply it.
- `output_dir` (Optional[str]): Directory to write the encrypted file. Defaults to the same directory as the input file.
- `output_filename` (Optional[str]): Custom filename for the encrypted file. Defaults to appending `.enc` to the original filename.
- `return_as_data` (bool): If True, returns the encrypted content as bytes instead of writing to disk.

Returns:
- Dictionary containing:
  - `encrypted_file_path` (str) or `encrypted_data` (bytes) – depending on the mode.
  - `ciphertext` (bytes): The Kyber ciphertext.
  - `shared_secret` (bytes): Shared secret used for symmetric encryption.

#### decrypt_file(encrypted_file: str, ciphertext: bytes, private_key: Optional[bytes] = None, output_dir: Optional[str] = None, output_filename: Optional[str] = None, return_as_data: bool = False)
Decrypt an encrypted file using Kyber and the selected symmetric cipher.

```python
result = pqfe.decrypt_file("document.txt.enc", ciphertext, private_key=private_key)
```

Parameters:
- `encrypted_file` (str): Path to the encrypted file.
- `ciphertext` (bytes): The Kyber ciphertext obtained during encryption.
- `private_key` (Optional[bytes]): Private key for decryption. If not provided, users should load or supply it.
- `output_dir` (Optional[str]): Directory to write the decrypted file. Defaults to the same directory as the encrypted file.
- `output_filename` (Optional[str]): Custom filename for the decrypted file. Defaults to the original filename (removing `.enc`).
- `return_as_data` (bool): If True, returns the decrypted content as bytes instead of writing to disk.

Returns:
- Dictionary containing:
  - `decrypted_file_path` (str) or `decrypted_data` (bytes) – depending on the mode.

### Supported Symmetric Ciphers

- **AES256GCM**: Default symmetric cipher providing AES-256 in GCM mode.
- **ChaCha20Poly1305**: An alternative symmetric cipher offering excellent performance and security.

### Supported Kyber Variants

- `Kyber512`: 128-bit classical / 64-bit quantum security.
- `Kyber768`: 192-bit classical / 96-bit quantum security.
- `Kyber1024`: 256-bit classical / 128-bit quantum security.

### Error Handling

The API may raise the following exceptions:

- `ValueError`: Invalid parameters or configuration.
- `FileNotFoundError`: File or key not found.
- `EncryptionError`: Encryption operation failed.
- `DecryptionError`: Decryption operation failed.
- `KeyError`: Key management operation failed.

Example error handling:

```python
try:
    result = pqfe.encrypt_file("document.txt", public_key=public_key)
except FileNotFoundError:
    print("File not found")
except ValueError as e:
    print(f"Invalid parameter: {e}")
```
