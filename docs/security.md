# Security Guidelines

## Overview

PQFE is designed with security as a primary concern, implementing post-quantum cryptography to protect against both classical and quantum computer attacks.

## Cryptographic Components

### Kyber

PQFE uses Kyber for key encapsulation, a lattice-based KEM that is a finalist in the NIST Post-Quantum Cryptography standardization process.

Security levels:
- Kyber512: NIST Level 1 (128-bit classical / 64-bit quantum security)
- Kyber768: NIST Level 3 (192-bit classical / 96-bit quantum security)
- Kyber1024: NIST Level 5 (256-bit classical / 128-bit quantum security)

### Hybrid Encryption

Files are encrypted using a hybrid scheme:
1. Kyber generates a shared secret
2. The shared secret is used with AES-256-GCM for file encryption
3. The Kyber ciphertext is stored alongside the encrypted file

## Key Management

### Storage

- Keys are stored in a protected directory with appropriate permissions
- Private keys are never transmitted or stored in plaintext
- Key files are encrypted at rest
- Regular key rotation is recommended

### Best Practices

1. Use strong access controls for key storage
2. Implement key rotation policies
3. Back up keys securely
4. Never share private keys
5. Use environment variables for key paths

## File Operations

### Encryption Process

1. Generate random AES key using Kyber
2. Encrypt file using AES-256-GCM
3. Store metadata securely
4. Protect file integrity with HMAC

### Secure Deletion

- Implement secure wiping of sensitive data
- Clear memory after operations
- Use appropriate file permissions

## Implementation Security

### Memory Safety

- Clear sensitive data from memory after use
- Avoid logging sensitive information
- Use secure memory wiping functions

### Error Handling

- Do not expose sensitive information in error messages
- Implement proper error recovery
- Log security-relevant events

### Side-Channel Protection

- Constant-time operations where possible
- Memory access patterns considered
- Protection against timing attacks

## Security Recommendations

1. Choose appropriate Kyber variant:
   - Kyber512: General use
   - Kyber768: Sensitive data
   - Kyber1024: High-security requirements

2. Key Management:
   - Rotate keys regularly
   - Secure backup procedures
   - Access control implementation

3. Operational Security:
   - Regular security audits
   - Monitor for suspicious activity
   - Keep dependencies updated

## Reporting Security Issues

If you discover a security vulnerability:

1. Do NOT open a public issue
2. Email info@solathomas.com
3. Include detailed information
4. Allow time for response and patch

## Security Updates

- Subscribe to security notifications
- Monitor NIST PQC announcements
- Keep PQFE updated to latest version 