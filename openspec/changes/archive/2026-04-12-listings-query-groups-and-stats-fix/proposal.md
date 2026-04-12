# Proposal: Listings Query Groups & Stats Hover Fix

## What
Two user-facing improvements:

1. **Listings page redesign** – Group all listings by query name. Each group is collapsible (click header to expand). Listing titles become clickable links to the eBay item. The dedicated "Link" column is removed.

2. **Stats hover crash fix** – Hovering over the price-trend chart crashes the page with `TypeError: i.toFixed is not a function`. Root cause: the Pydantic schema uses `Decimal` which JSON-serialises as a string, but the Recharts tooltip formatter assumes a `number` and calls `.toFixed()` directly. Additionally, two related bugs are fixed simultaneously: (a) the URL query param is named `granularity` in the frontend but the backend expects `interval`, and (b) the frontend type/chart key uses `period` while the backend returns `date`.

## Why
- The stats crash is a hard blocker — hovering the chart triggers an unhandled exception that unmounts the page.
- Listing groups improve navigation significantly: users track multiple queries and currently cannot distinguish which query each listing belongs to.

## Scope
- `backend/app/schemas/stats.py` — change `Decimal | None` → `float | None` for price fields in `PriceTrendPoint`, `SoldTrendPoint`, `QuerySummary` (fixes JSON serialisation)
- `frontend/src/api/client.ts` — fix `PriceTrendPoint.period` → `date`; fix URL params `granularity` → `interval` for stats endpoints
- `frontend/src/components/ui/PriceTrendChart.tsx` — fix `XAxis dataKey` + tooltip formatter null/type guard; add date formatting for X axis labels
- `frontend/src/components/ui/ListingTable.tsx` — title becomes `<a>` link; remove Link column
- `frontend/src/api/hooks.ts` — add optional `enabled` option to `useListings`
- `frontend/src/pages/Listings.tsx` — rewrite to query-group accordion layout
