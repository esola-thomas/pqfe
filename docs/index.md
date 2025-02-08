# Post-Quantum File Encryption (PQFE)

A secure post-quantum encryption system utilizing Kyber for file-based encryption and decryption operations.

## Overview

PQFE is a Python library that provides post-quantum secure file encryption using the Kyber key encapsulation mechanism (KEM). It is designed to be easy to use while maintaining strong security guarantees for protecting files against future quantum computer attacks.

## Features

- Post-quantum secure file encryption using Kyber
- Support for multiple Kyber variants (Kyber512, Kyber768, Kyber1024)
- Simple API for file encryption and decryption
- Secure key management
- Hybrid encryption scheme (Kyber + AES-256-GCM)
- Comprehensive error handling
- Performance benchmarking tools

## Quick Start

```python
from pqfe import PQFE

# Initialize with desired Kyber variant
pqfe = PQFE(variant="Kyber512")

# Generate keys
public_key, private_key = pqfe.generate_keys()

# Encrypt a file
result = pqfe.encrypt_file("document.txt", public_key)

# Decrypt the file
decrypted_path = pqfe.decrypt_file(result["encrypted_file_path"], private_key)
```

## Security Considerations

- Uses Kyber, a NIST PQC finalist for key encapsulation
- Implements hybrid encryption with AES-256-GCM
- Secure key storage and management
- Protection against side-channel attacks

## Documentation

- [Installation Guide](installation.md)
- [API Documentation](api.md)
- [Security Guidelines](security.md)

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details. 