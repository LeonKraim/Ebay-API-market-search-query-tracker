# Design: Listings Query Groups & Stats Hover Fix

## Stats crash – root cause analysis

The Recharts `<Tooltip formatter>` in `PriceTrendChart.tsx` is:
```ts
formatter={(v: number) => [`${symbol}${v?.toFixed(2)}`, '']}
```

Recharts passes `v` as whatever type the data field contains. Because `PriceTrendPoint.avg_price` (and the other price fields) are Pydantic `Decimal` fields, FastAPI serialises them as JSON **strings** (e.g. `"215.50"`). The TypeScript type claims `number | null` but the actual runtime value is a `string`. Strings have no `.toFixed` method → TypeError crash.

Secondary bugs fixed in the same pass:
- `client.ts` sends `?granularity=week` but the backend route param is named `interval` → backend silently ignores it and defaults to `day`
- `PriceTrendChart` uses `dataKey="period"` for XAxis but backend returns the field as `date` → X-axis labels are blank

## Fix strategy

### Backend
Change `Decimal | None` to `float | None` in `PriceTrendPoint`, `SoldTrendPoint`, `QuerySummary` (stats schemas only). `float` serialises as a JSON number. Pydantic `float` is sufficient precision for display purposes.

### Frontend – client.ts
- Rename `period: string` → `date: string` in `PriceTrendPoint` interface (matches backend field)
- Change URL param `granularity=` → `interval=` in `priceTrend` and `soldTrend` API calls

### Frontend – PriceTrendChart.tsx
- Fix `XAxis dataKey` to `"date"`
- Add `tickFormatter` to format ISO timestamps to short readable dates (`Apr 7`)
- Update tooltip `formatter` to coerce value to number with null guard

### Frontend – hooks.ts
Add optional `{ enabled?: boolean }` second argument to `useListings` so query groups can defer fetching until expanded.

## Listings redesign

### Layout
Replace the single flat table with a list of collapsible query-group cards:

```
[ ▶ Query name (keyword) ]      — collapsed
[ ▼ Query name (keyword) ]  42 listings
  ┌───────────────────────────────────────────┐
  │ listingTable rows (25 per page)           │
  └───────────────────────────────────────────┘
  [← Prev]  Page 1 / 2  [Next →]
```

### Data flow
1. `ListingsPage` fetches up to 100 queries via `useQueries(1, 100)`.
2. Each `<QueryGroup>` component manages its own expanded state and page state.
3. `useListings({ query_id: q.id, page, page_size: 25 }, { enabled: expanded })` is called per group — only fetches when the group is expanded.

### ListingTable changes
- Remove `ExternalLink` import and the Link column `<th>` + `<td>`
- Wrap title in `<a href={l.item_url} target="_blank" rel="noopener noreferrer">` with hover blue colour

### Security
All external links use `target="_blank" rel="noopener noreferrer"` to prevent tab-napping.
