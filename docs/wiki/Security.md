# Security & Privacy

YAMAN VIRAL STUDIO PRO is local-first, but local-first does not automatically mean secure or fully offline. The current Windows launcher binds Uvicorn to 127.0.0.1:8765. Keep this boundary unless a hardened deployment is deliberately implemented.

## Current security controls found in source

- YouTube source URL host allowlist for the download workflow.
- Download size limit through MAX_DOWNLOAD_MB.
- Workspace path containment check for Auto-Editor source files.
- OAuth state validation and expiry.
- TikTok OAuth PKCE verifier/challenge.
- Fernet encryption for OAuth tokens, OAuth app credentials and visual-provider API keys.
- Explicit confirm_publish requirement before platform upload.
- User-approved updater flow with expected commit validation.

## Important limitations

- The inspected application does not show a general user login/session authorization layer protecting all API routes.
- The workspace is mounted as static content under /workspace.
- OAuth encryption defaults to a local .oauth.key file unless YAMAN_TOKEN_ENCRYPTION_KEY is supplied.
- A local process or user account with access to the machine may be able to access local files and keys.
- A development server exposed to a LAN or public internet is not a production deployment.

**Do not expose this version directly to the public internet.** A reverse proxy alone does not replace application authentication and authorization.

## Recommended hardening before shared/production use

1. Add authentication and role-based authorization to every sensitive route.
2. Restrict workspace file access; avoid serving private source media and generated assets without authorization.
3. Move encryption keys to OS-protected secret storage or a dedicated secret manager.
4. Add CSRF protections where browser cookie sessions are used.
5. Validate OAuth redirect URI, state, PKCE and minimum scopes for every provider.
6. Add rate limiting, request size limits and strict URL/SSRF defenses.
7. Redact secrets and personal data from logs.
8. Add audit events for credential changes, exports, deletes and publishing.
9. Use HTTPS, secure headers, firewall rules and least-privilege service accounts.
10. Test dependency vulnerabilities and backup restoration.

## Incident response

If a key or token is exposed, revoke it with the provider, rotate the credential, replace the encryption key as part of a controlled vault migration, and inspect logs and repository history. Do not merely delete the visible secret from the latest commit.

## Media rights

Import, transform and publish only media for which the user has the required rights. Platform API access does not grant copyright permission.
