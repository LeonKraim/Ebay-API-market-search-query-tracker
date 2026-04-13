# Proposal: Hybrid Sold Tracking

## What
Implement a hybrid approach for sold/completed listing detection:
1. **Disappearance tracking** — Track listings that disappear between Browse API snapshots and infer them as "ended/sold," recording them in `sold_records` with `source='disappeared'`.
2. **Hardened scraper** — Add CAPTCHA detection, rotating User-Agents, and randomized delays to the existing HTML scraper so it doesn't silently fail.

## Why
The app's core purpose is tracking what sold and what didn't. The current scraper-only approach silently fails when eBay serves a CAPTCHA (200 OK page with no parseable items), causing total data loss with no detection or recovery. The Browse API doesn't support completed/sold listing filters, and eBay's Marketplace Insights API is restricted to approved developers. The hybrid approach adds an API-based baseline that works 100% through official channels while hardening the scraper as a supplementary data source.

## Research
- eBay Browse API `item_summary/search` has no `completed`/`sold` filter — confirmed via official docs.
- eBay Marketplace Insights API (`buy/marketplace_insights`) has `lastSoldDate` filter but is "restricted and not open to new users."
- eBay Finding API `findCompletedItems` is being deprecated (docs redirect to homepage).
- Disappearance-based tracking is a well-known pattern in marketplace monitoring (items that drop off active results are inferred as ended/sold).
