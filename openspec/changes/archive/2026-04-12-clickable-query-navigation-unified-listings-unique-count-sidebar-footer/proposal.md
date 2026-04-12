# Proposal: Clickable query navigation, unified market tab, unique item counts, and sidebar cleanup

## What Changes

Implement five related product changes across the frontend shell and stats backend:

1. Make visible query surfaces clickable so selecting a query opens the market browser automatically on that query's listings.
2. Merge the current Listings and Sold top-level destinations into one market-browsing tab with an in-page live/sold mode switch.
3. Remove the top-left product wordmark from the sidebar so the left rail only shows navigation destinations plus status/footer content.
4. Change the items-evaluated metric to count unique items instead of summing duplicate live and sold records.
5. Add a small `made by leon kraim` footer note in the lower left sidebar area.

## Why

- Query objects are currently visually prominent but dead-end UI; users should be able to jump directly from a query to the results browser.
- Listings and sold results are two views of the same browsing workflow and do not need separate top-level sidebar slots.
- The sidebar currently spends permanent space on branding while the user asked for a cleaner destination-only rail.
- The current items-evaluated count double counts repeated snapshots and sold/live overlap, which makes the headline metric misleading.
- The footer credit is a simple shell-level branding requirement and fits naturally in the sidebar.

## Referenced best-practice sources

- Material Design navigation drawer guidance: drawers should prioritize clear destination items and active-state switching between app views.
  - https://m3.material.io/components/navigation-drawer/guidelines
  - https://m3.material.io/components/navigation-drawer/overview
- MDN URL and History APIs: query-string state should be represented with `URLSearchParams`, and same-origin page-state changes can be reflected via `history.pushState()` without reloading the document.
  - https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams
  - https://developer.mozilla.org/en-US/docs/Web/API/History/pushState
- SQLAlchemy set-operation guidance: aggregate counts across multiple sources should be composed with `select()`, set operations such as `UNION`, and aggregate functions rather than duplicating rows in application code.
  - https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#union-union-all-and-other-set-operations

## Acceptance criteria

1. Clicking a query card or recent-query row opens the market browser on the live listings view and expands the selected query automatically.
2. The sidebar exposes a single market-browsing destination instead of separate Listings and Sold destinations.
3. The sidebar no longer shows the `eBay Intel` wordmark, and it shows `made by leon kraim` in the lower left footer area.
4. The unified market page lets users switch between live listings and sold records without leaving the page.
5. The items-evaluated metric shows the count of unique item IDs across live and sold data, not the sum of raw rows.
6. The final browser verification shows the new sidebar, clickable query navigation, unified market tab, and unique metric without console errors.