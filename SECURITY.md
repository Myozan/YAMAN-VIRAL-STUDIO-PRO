# Security Policy

## Security posture

YAMAN VIRAL STUDIO PRO v1.8.0 is intended for local use. The Windows launcher binds to loopback. The current application does not include a universal authentication/session and role-based authorization layer protecting every sensitive API route, and workspace files are mounted as static content.

**Do not expose v1.8.0 directly to a LAN or public internet.** HTTPS or a reverse proxy alone does not provide application-level authorization.

See [Security, Privacy & Deployment Safety](docs/wiki/Security.md) for verified controls, known gaps, deployment boundaries and the production-hardening checklist.

## Supported version

Security reports are welcome for the current maintained branch and latest published release. Include the affected version and deployment configuration.

## Reporting a vulnerability

Please do not publish exploitable vulnerabilities, access tokens, OAuth secrets, personal data or private media in a public issue.

Use GitHub's **Private vulnerability reporting** feature on this repository if enabled. If unavailable, contact the repository owner privately through the contact method listed on the GitHub profile.

Include:
- A concise description of the vulnerability and potential impact.
- Steps to reproduce or a proof of concept that does not expose real user data.
- Affected files, versions and configuration.
- Suggested mitigation, if known.

Please allow reasonable time for investigation and remediation before public disclosure. Do not perform destructive testing against systems you do not own or have explicit permission to assess.

## Sensitive data

Never commit `.oauth.key`, OAuth tokens, provider credentials, `.env` files, local settings, private videos or workspace data. Revoke exposed credentials immediately. Removing a secret from the latest commit is not sufficient; rotate it and assess repository history and issued tokens.
