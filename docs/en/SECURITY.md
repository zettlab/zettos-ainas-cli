# Security reporting

**English** · [简体中文](../../SECURITY.md) · [Documentation](README.md)

Do not put passwords, tokens, device identifiers, private content, or exploitable vulnerability details in a public issue.

Use [GitHub private vulnerability reporting](https://github.com/zettlab/zettos-ainas-cli/security/advisories/new). If it is unavailable, use the official support entry on the Zettlab website to request a security contact; do not post vulnerability details publicly.

Include affected CLI/firmware versions, reproduction steps, required privileges, and potential impact. Attach minimal redacted material and test only devices you are authorized to assess.

Beta security fixes will be delivered in new signed Releases. There is no long-term support commitment today. The installer verifies signatures and file digests. The private signing key is excluded from this repository and its archives.

## Dependency review

The first candidate updated TLS, certificate, and other dependencies with known issues. `rsa 0.9.10` remains affected by [RUSTSEC-2023-0071](https://rustsec.org/advisories/RUSTSEC-2023-0071.html), a timing-leakage advisory for RSA private-key operations with no patched version identified in the recorded audit.

The CLI only uses the NAS RSA **public key** to encrypt the login password. It holds no RSA private key and performs no RSA decryption or signing. A bounded exception applies to this usage and must be reviewed on usage/version changes or by 2027-05-01. This is not a zero-vulnerability claim or a security assessment of the NAS server's private-key implementation.
