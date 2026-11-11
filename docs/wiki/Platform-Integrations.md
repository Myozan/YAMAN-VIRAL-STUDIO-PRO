# Platform Integrations

YAMAN VIRAL STUDIO PRO contains optional integration paths for YouTube, Instagram and TikTok publishing, plus Runway/Pexels visual providers. Each integration depends on provider credentials, account eligibility, network access and the provider's current API policies.

## YouTube

- OAuth provider: Google.
- Config environment variables: YAMAN_GOOGLE_CLIENT_ID and YAMAN_GOOGLE_CLIENT_SECRET.
- OAuth scope used by the current code: youtube.upload.
- Publishing flow: YouTube Data API resumable upload.
- Privacy values supported by the publish request: private, unlisted, public.
- API quota, channel restrictions and Google project verification may affect availability.

## Instagram

- OAuth provider: Meta.
- Config environment variables: YAMAN_META_APP_ID and YAMAN_META_APP_SECRET.
- The current OAuth flow requests Instagram and Facebook Page-related scopes.
- Account discovery expects an Instagram professional account connected to a Facebook Page.
- Publishing and insights depend on Meta app permissions, review and account eligibility.
- Personal-account support must not be assumed.

## TikTok

- OAuth provider: TikTok.
- Config environment variables: YAMAN_TIKTOK_CLIENT_KEY and YAMAN_TIKTOK_CLIENT_SECRET.
- OAuth flow includes PKCE.
- Creator information is queried before publishing to obtain available privacy settings and duration constraints.
- Direct Post capability, app review and creator consent can restrict publishing.

## Visual providers

- Runway API key can be supplied through RUNWAY_API_KEY or encrypted local provider settings.
- Pexels API key can be supplied through PEXELS_API_KEY or encrypted local provider settings.
- Visual provider configuration is optional; local motion graphics remain a separate path.
- Cloud providers may incur charges and send prompts/media to external systems. Review provider terms and privacy implications.

## Credential storage

OAuth application credentials, OAuth tokens and visual provider keys are encrypted using Fernet. The default key file is .oauth.key unless YAMAN_TOKEN_ENCRYPTION_KEY is provided. Back up encryption keys and vault files together; losing the key can make encrypted credentials unrecoverable.

## Operational rules

- Use official provider APIs; do not bypass review, OAuth or platform restrictions.
- Request only required scopes.
- Keep redirect URIs exact and stable.
- Reauthorize after revocation or unrecoverable token expiry.
- Respect rate limits, upload size, duration and content rules.
- Require explicit user confirmation before publication.
- Never promise public auto-posting until the provider app has the required permissions and review status.
