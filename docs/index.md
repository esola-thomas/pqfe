# Post-Quantum File Encryption (PQFE)

A secure post-quantum encryption system utilizing Kyber for file-based encryption and decryption operations. The library implements a hybrid encryption scheme that combines post-quantum key encapsulation with a modern symmetric cipher, ensuring both strong security and efficient file handling.

## Overview

PQFE is a Python library that provides post-quantum secure file encryption using the Kyber key encapsulation mechanism (KEM). Its modular design allows for the selection of different Kyber variants and symmetric ciphers (AES256GCM or ChaCha20Poly1305) to fit varying security and performance requirements.

## Features

- **Post-Quantum Security:**  
  Uses Kyber (a NIST PQC finalist) for secure key encapsulation.
- **Hybrid Encryption:**  
  Combines Kyber with a modern symmetric cipher for efficient file encryption.
- **Pluggable Symmetric Ciphers:**  
  Default is AES256GCM; users can choose ChaCha20Poly1305 as an alternative.
- **Flexible File I/O:**  
  Supports configurable output directories, custom filenames, and in-memory operations.
- **Secure Key Management:**  
  Integrated key generation and loading from a secure storage directory.
- **Comprehensive Error Handling:**  
  Detailed exceptions to facilitate debugging and secure usage.

## Quick Start

```python
from pqfe import PQFE

# Initialize PQFE with Kyber512 and default AES256GCM symmetric cipher
pqfe = PQFE(variant="Kyber512")

# Generate keys
public_key, private_key = pqfe.generate_keys()

# Encrypt a file (results include Kyber ciphertext and shared secret)
result = pqfe.encrypt_file("document.txt", public_key=public_key)

# Decrypt the file
decrypted = pqfe.decrypt_file(result["encrypted_file_path"], result["ciphertext"], private_key=private_key)
```

## Security Considerations

- Utilizes Kyber for robust post-quantum key encapsulation.
- Implements a hybrid encryption model combining Kyber with AES256GCM (or ChaCha20Poly1305).
- Secure key storage and management with configurable directories.
- Designed to protect against both classical and quantum attacks.

## Documentation

- [Installation Guide](installation.md)
- [API Documentation](api.md)
- [Security Guidelines](security.md)

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.
