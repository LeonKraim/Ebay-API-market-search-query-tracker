# Proposal: eBay Global Site Selector

## What
Add a global eBay marketplace selector to the Settings page that lets users choose which eBay site to use (US, UK, Germany, France, Australia, Canada, etc.). The selected site becomes the default `ebay_site_id` in `config.toml` and is also sent as `GLOBAL-ID` in Finding API calls.

Additionally, convert the per-query Site ID field from a free-text input to a dropdown matching the same list of supported eBay sites.

## Why
eBay operates regional marketplaces (EBAY-US, EBAY-GB, EBAY-DE, EBAY-FR, EBAY-AU, etc.). The current app defaults to EBAY-GB and only lets users type a raw site ID string in the query form. This is error-prone and the user has discovered that the EBAY-GB endpoint is currently returning HTTP 500 errors, while EBAY-DE works. A proper site selector on the Settings page (and dropdown on the query form) gives users an easy way to switch between markets.

## Best Practice Sources
1. **eBay Finding API docs** — The `GLOBAL-ID` parameter accepts standard site IDs like EBAY-US, EBAY-GB, EBAY-DE, etc. (https://developer.ebay.com/devzone/finding/callref/Enums/GlobalIdList.html)
2. **eBay Global ID list** — Canonical list of supported marketplace IDs used across all eBay APIs
3. **Pattern**: Settings-driven defaults with per-entity overrides is the standard pattern for multi-tenant/multi-region SaaS apps (Stripe dashboard region selector, Shopify market selector)

## Scope
- Backend: Add `PUT /config/ebay-site` endpoint to update `config.toml` and reload settings
- Backend: Define canonical list of supported eBay site IDs
- Frontend Settings page: Add dropdown to select global eBay site
- Frontend Queries form: Replace free-text Site ID input with dropdown
- Tests: Update existing tests, add new tests for the config endpoint
