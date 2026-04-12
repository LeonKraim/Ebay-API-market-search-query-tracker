# Design: Clickable query navigation, unified market tab, unique item counts, and sidebar cleanup

## Summary

This change is a shell/navigation refresh with one stats correctness fix. The implementation keeps the current single-page app structure, but upgrades its page state so navigation intent can carry a selected query and market mode through the URL.

## URL-backed page state

- The app currently stores the active page only in component state.
- Introduce a lightweight page-state layer in `App.tsx` backed by `window.location.search` and `history.pushState()`.
- Persist at least these values in the URL:
  - `page`
  - `queryId` for direct navigation into a query's market results
  - `market` for `live` vs `sold` mode within the unified market page
- Read initial state from the URL on load and respond to `popstate` so browser back/forward stays coherent.

## Query-driven navigation

- Make dashboard recent-query rows clickable.
- Make query cards on the Queries page clickable at the card container level.
- Preserve existing button actions for run/edit/delete by stopping event propagation on those controls.
- Navigating from a query surface should:
  - switch the app to the unified market page
  - default the market mode to `live`
  - pass the selected query ID so the correct accordion opens automatically

## Unified market page

- Replace separate `listings` and `sold` top-level pages with one top-level destination.
- Keep the current live-listings accordion experience for the live mode.
- Move sold browsing under the same page behind a local live/sold segmented toggle.
- For the live mode:
  - preserve query accordions, list/grid toggle, and pagination
  - auto-expand the selected query from URL state
- For sold mode:
  - keep the current sold search and pagination behavior
  - show it as a sibling mode inside the unified page rather than a separate route/destination

## Sidebar cleanup

- Remove the dedicated wordmark block from the top of the sidebar.
- Keep only navigation items, items-evaluated status, scheduler indicator, and the footer credit.
- Add the footer credit in the lower left beneath the status block.

## Unique items-evaluated metric

- The current endpoint sums all live rows plus all sold rows, which double counts:
  - repeated snapshot appearances of the same `item_id`
  - overlap where the same `item_id` exists in both live and sold tables
- Replace that with a database-side unique count over the union of non-null `item_id` values from `listing_records` and `sold_records`.
- Keep the response shape unchanged so the frontend can continue polling the same endpoint.
- Compute `since` as the earliest available observation timestamp across both sources.

## Verification plan

- Backend tests:
  - `items-evaluated` counts unique item IDs across live and sold rows.
  - earliest `since` timestamp is stable when only one side has data or both sides have data.
- Frontend verification:
  - clicking a query opens the market page on the matching live query accordion
  - the sidebar shows one market destination, no top-left wordmark, and the footer credit
  - live/sold switching works from the unified market page
  - the displayed items-evaluated total matches unique data semantics