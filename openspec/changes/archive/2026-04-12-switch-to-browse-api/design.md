## Context

The backend currently uses the eBay Finding API (XML, `SECURITY-APPNAME` auth) to fetch listings. This API is rate-limited for our credentials. The eBay Browse API (JSON, OAuth Bearer token auth) works with the same credentials and returns richer data. The `RawListing` dataclass and `fetch_all_listings()` function are imported by 8+ files — their public interface must remain identical.

## Goals / Non-Goals

**Goals:**
- Replace Finding API XML client with Browse API JSON client in `ebay_finding.py`
- Maintain identical `RawListing` fields and `fetch_all_listings()` signature
- Convert marketplace IDs from hyphen format (`EBAY-DE`) to underscore format (`EBAY_DE`) for Browse API headers
- Rewrite unit tests and fixtures for JSON responses
- Keep all retry/backoff logic intact

**Non-Goals:**
- Renaming `ebay_finding.py` to `ebay_browse.py` (avoid import churn across 8+ files)
- Adding new fields from Browse API (e.g., `shortDescription`, `categories`) — future work
- Changing `results_per_page` config default (keep 100, Browse API allows up to 200)

## Decisions

### 1. Keep file name `ebay_finding.py`
**Rationale:** 8+ files import from `app.services.ebay_finding`. Renaming would create unnecessary churn with zero functional benefit.

### 2. Convert `EBAY-DE` → `EBAY_DE` inside `_fetch_page` only
**Rationale:** The rest of the codebase (DB, frontend, config) uses hyphen format. Conversion to underscore happens at the HTTP call boundary only via `site_id.replace("-", "_")`.

### 3. Map Browse API `buyingOptions` to existing `listing_type` / `buy_it_now` fields
- `buyingOptions: ["FIXED_PRICE"]` → `listing_type="FixedPrice"`, `buy_it_now=True`
- `buyingOptions: ["AUCTION"]` → `listing_type="Auction"`, `buy_it_now=False`
- `buyingOptions: ["FIXED_PRICE", "BEST_OFFER"]` → `listing_type="FixedPrice"`, `buy_it_now=True`

### 4. Use `legacyItemId` for `item_id` field
**Rationale:** The existing DB stores numeric eBay item IDs. `legacyItemId` provides the traditional format. `itemId` in Browse API is a different encoded format (`v1|123456|0`).

### 5. Offset-based pagination replacing page-based
- Finding API: `paginationInput.pageNumber` (1-indexed)
- Browse API: `offset` (0-indexed) + `limit`
- `offset = (page - 1) * page_size` where `page` is internal loop counter
- Total pages calculated from `response["total"]`: `ceil(total / limit)`

### 6. Include both auction and fixed-price listings
- Add `filter=buyingOptions:{AUCTION|FIXED_PRICE}` to request params
- Without this filter, Browse API only returns FIXED_PRICE by default

## Risks / Trade-offs

- **OAuth token expiry** → User must refresh the Bearer token in `.env` when it expires. Future enhancement: add OAuth client_credentials flow for automatic refresh.
- **Browse API max 10,000 items** → Acceptable for market intelligence use case. Finding API had similar practical limits.
- **`itemSummaries` may be absent in response** → Handle gracefully: treat missing key as empty list (0 results).
- **`sellingState` not directly available in Browse API** → Map to "Active" for all returned items (Browse API only returns active listings by default).
