# Security, Privacy & Deployment Safety

**Security posture: local-use only for v1.8.0.** YAMAN VIRAL STUDIO PRO is local-first, but local-first is not synonymous with offline, authenticated or production-secure.

## 1. Supported deployment boundary

The Windows launcher binds the application to `127.0.0.1:8765`. Preserve loopback binding. Do not expose this release directly to a LAN, reverse proxy or public internet.

The current application does not provide a general authentication/session and role-based authorization layer covering every sensitive API route. The `/workspace` directory is mounted as static content. A reverse proxy, firewall rule or HTTPS certificate does not compensate for missing application-level authorization.

<badge color="danger">Not production-hardened for shared or public access</badge>

## 2. Verified controls in v1.8.0

The inspected source includes the following controls in specific workflows:

- YouTube source URL host allowlist in the download workflow.
- Download size limit controlled by `MAX_DOWNLOAD_MB`.
- Workspace path containment for Auto-Editor source files.
- OAuth state validation and expiry; TikTok OAuth uses PKCE.
- Fernet encryption for OAuth tokens, OAuth app credentials and visual-provider API keys.
- Explicit `confirm_publish` requirement before platform upload.
- User-approved updater flow with expected-commit validation.

These controls are scoped protections. They must not be interpreted as a complete application security boundary.

## 3. Known gaps and risk register

| Area | Current state | Risk / required action |
|---|---|---|
| Authentication | No universal login/session guard | Add authentication before multi-user or remote access |
| Authorization | No complete role/ownership policy on every route | Enforce deny-by-default permissions per resource |
| Workspace media | Static mount exposes workspace files to anyone who can reach the app | Replace with authenticated file delivery and per-user path checks |
| Secrets | Local `.oauth.key` fallback may be used | Prefer OS-protected secret storage; define rotation and recovery |
| Browser sessions | No complete CSRF/session policy | Add CSRF protection if cookie sessions are introduced |
| Network | Loopback launcher is the intended boundary | Keep firewall restricted; do not change host binding casually |
| Abuse controls | No complete global rate-limit policy verified | Add request limits, rate limits and upload quotas |
| Auditability | No comprehensive security audit trail verified | Record credential, export, delete and publishing events |
| Supply chain | Dependency checks are not a complete security gate | Add dependency vulnerability scanning and pinned release artifacts |
| Recovery | Backup guidance exists; restore must be rehearsed | Test encrypted-secret recovery and workspace restore |

## 4. Required production-hardening sequence

1. **Identity:** implement secure login, session lifecycle, password hashing or trusted identity provider, MFA for administrators.
2. **Authorization:** add deny-by-default role and resource ownership checks to every sensitive API route.
3. **Private media:** remove public static access to private workspace content; use authenticated, short-lived downloads.
4. **Secrets:** store encryption keys outside the repository and ordinary config files; document rotation and recovery.
5. **Request safety:** CSRF protection for cookie sessions, strict CORS, content-type and request-size limits, rate limits.
6. **Network:** HTTPS, secure headers, firewall allowlists and least-privilege service account.
7. **Input validation:** SSRF-safe URL fetching, canonical path checks, safe archive extraction and subprocess argument validation.
8. **Observability:** redact tokens and personal data; add tamper-aware audit events and security alerting.
9. **Supply chain:** dependency scanning, secret scanning, signed release artifacts and reproducible build checks.
10. **Verification:** automated security regression tests, dependency review, threat-model review and backup/restore drill.

## 5. Operator checklist

- [ ] Keep the listener on loopback.
- [ ] Keep the repository and workspace private.
- [ ] Never commit `.env`, `.oauth.key`, `settings.local.json`, tokens, credentials or private media.
- [ ] Use unique provider credentials with minimum required scopes.
- [ ] Revoke exposed tokens immediately; rotate the encryption key through a controlled migration.
- [ ] Back up workspace data and verify restoration on a separate copy.
- [ ] Review logs before sharing diagnostics; redact personal data and secrets.
- [ ] Confirm rights to all imported and published media.

## 6. Vulnerability reporting

Please do not publish exploitable vulnerabilities, access tokens, OAuth secrets, personal data or private media in a public issue.

Use GitHub's **Private vulnerability reporting** feature when enabled. Otherwise contact the repository owner privately through the contact method listed on the GitHub profile. Include impact, affected version/files, reproduction steps and a suggested mitigation. Allow reasonable time for investigation and remediation before public disclosure.

## 7. Incident response

If a credential is exposed: revoke it with the provider, rotate it, inspect access and repository history, preserve relevant logs, and assess whether private media or user data was accessed. Removing a secret from the latest commit is not sufficient; historical copies and issued tokens must also be addressed.

## 8. Media rights and privacy

Only import, transform and publish media for which the operator has the required rights. Platform API access does not grant copyright permission. Treat transcripts, source videos, generated media and OAuth credentials as private workspace data.

## Related documentation

- [Security Policy](../../SECURITY.md)
- [Operations Runbook](../OPERATIONS-RUNBOOK.md)
- [Testing Strategy](../TESTING-STRATEGY.md)
