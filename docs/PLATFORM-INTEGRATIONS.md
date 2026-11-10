# Platform Integration Plan

## YouTube
- Authorization: Google OAuth 2.0; request only the scopes required for selected actions.
- Publishing: YouTube Data API video upload endpoint; resumable upload and status tracking.
- Analytics: YouTube Analytics API for authorized channel/video reports.
- UI states: Not connected, Authorization pending, Connected, Needs reauthorization, Revoked, Quota limited, Error.
- Persist channel identity, granted scopes, token expiry, encrypted refresh token, last sync, and quota state.
- Do not assume every account/project can publish publicly immediately; account verification, API project status, and platform policy can affect behavior.

## Instagram
- Eligibility: supported Instagram professional account and the required Meta app/account setup.
- Publishing: Instagram Graph API publishing flow for supported media types.
- Analytics: Insights metrics exposed for the account and media type.
- UI states mirror YouTube, with eligibility and permission diagnostics.
- Do not promise support for personal accounts or unsupported media/metrics.

## TikTok
- Authorization: TikTok Login Kit/OAuth and approved Content Posting API scopes.
- Publishing: Direct Post or upload-to-draft flow according to granted capability and app review status.
- Analytics: use only metrics available to the authorized app/product and account.
- Check creator info and posting constraints before upload; handle user consent and post status.
- Unreviewed clients may be restricted; do not claim public auto-posting until the app has the required approval.

## Common adapter contract
Each adapter should implement:
- begin_oauth(), handle_oauth_callback(), refresh_credentials(), disconnect()
- get_account_profile(), get_capabilities()
- validate_media(), create_publish_job(), get_publish_status()
- fetch_analytics(), get_rate_limit_state()

All methods return normalized domain objects plus provider-specific raw response references. Provider errors must be mapped to retryable, authorization, validation, quota, or permanent categories.

## SEO metadata normalization
Common internal fields:
- title (nullable; platform-dependent)
- caption
- description
- keywords[]
- hashtags[]
- tags[] (only where the platform supports tags)
- language
- category (where supported)
- call_to_action
- cover_asset_id
- alt_text (where supported)
- platform_options (validated provider-specific fields)

The UI must explain which fields will actually be sent to each platform. Never silently map a generic "tag" to an unsupported platform field.

## API governance
- Respect provider terms, API quotas, rate limits, retention rules, and review requirements.
- Store timestamps and data freshness.
- Avoid scraping private analytics or using unofficial endpoints.
- Do not use browser automation to bypass OAuth, API review, or platform publishing controls.
