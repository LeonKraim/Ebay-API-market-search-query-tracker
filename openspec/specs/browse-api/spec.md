# browse-api Specification

## Purpose
TBD - created by archiving change switch-to-browse-api. Update Purpose after archive.
## Requirements
### Requirement: OAuth token MUST be obtained via client_credentials grant

The system SHALL obtain OAuth 2.0 Application Access Tokens via eBay's client_credentials grant flow.

**Purpose:** Provide standards-compliant authentication for Browse API calls.
**Implementation:** Implement `_get_access_token(app_id, cert_id)` function in `ebay_finding.py` module.

#### Scenario: Request OAuth token
- The system MUST POST to `https://api.ebay.com/identity/v1/oauth2/token`
- The system MUST include Authorization header: `Basic {base64(app_id:cert_id)}`
- The system MUST send Body: `grant_type=client_credentials&scope=https://api.ebay.com/oauth/api_scope`
- THEN the system SHALL receive `access_token` in Bearer format, valid for 7200 seconds

#### Scenario: Cache and reuse valid tokens
- The system MUST store OAuth token in module with expiry timestamp
- The system MUST check if token is still valid (60s safety margin) before making requests
- The system SHALL reuse token if valid; only request new one if expired
- Result: Reduced latency, fewer OAuth requests

### Requirement: System MUST support Browse API JSON client for listings fetching

The system SHALL implement JSON-based Browse API integration for fetching eBay listings (module `app.services.ebay_finding`).

**Purpose:** Provide access to eBay listings via the available Browse API.
**Implementation:** Implement JSON parsing, offset-based pagination, OAuth Bearer token authentication in `ebay_finding.py`.

#### Scenario: Fetch listings from Browse API
- The system MUST GET from `https://api.ebay.com/buy/browse/v1/item_summary/search`
- The system MUST include Authorization: `Bearer {oauth_token}`
- The system MUST include Header: `X-EBAY-C-MARKETPLACE-ID` (underscore format, e.g., `EBAY_DE`)
- The system MUST send Query params: `q`, `limit` (max 200), `offset`, `sort=newlyListed`, `filter=buyingOptions:{AUCTION|FIXED_PRICE}`
- THEN the system SHALL receive JSON response with `total` count and `itemSummaries` array

#### Scenario: Parse Browse API JSON items
- The system MUST extract: `legacyItemId`, `price.value/currency`, `buyingOptions`, `bidCount`, `image.imageUrl`, `itemWebUrl`, `itemEndDate`, `itemLocation`, `title`
- The system MUST map: `FIXED_PRICE` → buy_it_now=True; `AUCTION` → buy_it_now=False
- The system MUST set: selling_state always "Active" (Browse API assumption)
- Result: RawListing objects compatible with existing dedup/polling logic

#### Scenario: Offset-based pagination
- The system MUST calculate total_pages = ceil(total_items / page_size)
- The system MUST iterate: offset = (page - 1) * page_size
- The system MUST fetch pages sequentially up to max_pages limit
- Result: All available listings within quota

### Requirement: Retry resilience MUST be implemented for Browse API

The system SHALL implement exponential backoff retry logic for transient Browse API failures.

**Purpose:** Maintain network resilience for Browse API calls.
**Implementation:** Exponential backoff for 429/5xx errors; fail-fast on 401/403 OAuth errors.

#### Scenario: Retry on rate limits (429)
- The system MUST use exponential backoff: delay * 2^(attempt-1)
- The system MUST wait configured backoff seconds between retries
- Result: Recover from temporary rate limits

#### Scenario: Retry on server errors (5xx)
- The system MUST use same exponential backoff as 429
- The system MUST re-attempt up to configured max_attempts
- Result: Recover from transient failures

#### Scenario: Fail fast on auth errors
- The system MUST NOT retry on 401 Unauthorized or 403 Forbidden
- The system MUST log error with status code immediately
- Result: OAuth issues surface without delay

### Requirement: OAuth token cache MUST be maintained with automatic expiry refresh

The system SHALL cache OAuth tokens and refresh them automatically when they expire.

**Purpose:** Optimize token reuse to minimize OAuth requests and latency.
**Implementation:** Module-level globals `_cached_token` and `_token_expires_at` with 60s safety margin.

#### Scenario: Initialize token cache at module load
- The system MUST initialize `_cached_token` to None
- The system MUST initialize `_token_expires_at` to 0.0
- Result: Ready for first token request

#### Scenario: Refresh token when expired
- The system MUST check token expiry before each fetch
- The system MUST call OAuth endpoint if expired or missing
- The system MUST store new token and expiry time
- Result: Always have valid token without explicit refresh calls

