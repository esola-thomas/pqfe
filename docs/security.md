# Security Guidelines

## Overview

PQFE is designed with security as a primary concern. It implements post-quantum cryptography to protect files against both classical and quantum computer attacks. The system leverages Kyber for key encapsulation and a hybrid encryption approach for file confidentiality and integrity.

## Cryptographic Components

### Kyber

PQFE uses Kyber, a lattice-based key encapsulation mechanism (KEM) and a finalist in the NIST Post-Quantum Cryptography standardization process.

Security levels:
- **Kyber512:** NIST Level 1 (128-bit classical / 64-bit quantum security)
- **Kyber768:** NIST Level 3 (192-bit classical / 96-bit quantum security)
- **Kyber1024:** NIST Level 5 (256-bit classical / 128-bit quantum security)

### Hybrid Encryption

Files are encrypted using a two-step process:
1. **Key Encapsulation with Kyber:**  
   Generates a shared secret along with a Kyber ciphertext.
2. **Symmetric Encryption:**  
   Uses the shared secret (processed through a KDF or truncated) with a symmetric cipher.
   - **Default Cipher:** AES256GCM.
   - **Alternative:** ChaCha20Poly1305.

This design allows for high performance when encrypting large files while ensuring robust security.

## Key Management

### Storage

- Keys are stored in a secure directory with appropriate file permissions.
- Private keys are protected from unauthorized access and are never transmitted in plaintext.
- It is recommended to enable encryption-at-rest for key storage and to use secure backup procedures.

### Best Practices

1. **Access Control:**  
   Ensure only authorized users have access to key directories.
2. **Key Rotation:**  
   Regularly rotate keys and securely back up new key pairs.
3. **Environment Variables:**  
   Use environment variables to configure key paths securely.

## File Operations Security

### Encryption Process

1. Generate a shared secret using Kyber.
2. Encrypt the file using the selected symmetric cipher.
3. Store the Kyber ciphertext alongside the encrypted file.
4. Optionally, include metadata to verify file integrity.

### Secure Deletion

- Securely wipe temporary files and sensitive data from memory.
- Use proper file permissions to limit access to decrypted content.

## Implementation Security

### Memory Safety

- Clear sensitive data from memory after use.
- Avoid logging raw keys or sensitive data.
- Utilize secure memory wiping functions where possible.

### Error Handling and Logging

- Do not expose sensitive information in error messages.
- Implement detailed logging for security-relevant events without revealing critical data.
- Use consistent error handling to avoid leakage of internal state.

### Side-Channel Protection

- Employ constant-time operations where feasible.
- Be mindful of memory access patterns to mitigate timing attacks.
- Regularly audit and update dependencies to mitigate emerging side-channel risks.

## Security Recommendations

1. **Variant and Cipher Selection:**  
   - Choose an appropriate Kyber variant based on your security requirements.
   - Consider using ChaCha20Poly1305 for environments where performance is critical and security is paramount.
2. **Operational Security:**  
   - Regularly review and update key management and encryption practices.
   - Perform periodic security audits and vulnerability assessments.
3. **Keep Dependencies Updated:**  
   - Monitor updates from cryptographic libraries and the NIST PQC process.
   - Stay informed about emerging threats and update PQFE accordingly.

## Reporting Security Issues

If you discover a security vulnerability:
If you discover a security vulnerability:
1. Open an issue on GitHub (https://github.com/esola-thomas/PQFE/issues) describing the vulnerability
2. Provide as much detail as possible about the vulnerability, including:
   - Steps to reproduce
   - Affected components
   - Potential impact
   - Any suggested mitigations
3. The maintainers will respond and work with you on a resolution

## Security Updates

- Subscribe to security notifications.
- Monitor NIST PQC announcements.
- Update to the latest PQFE version as improvements and patches are released.