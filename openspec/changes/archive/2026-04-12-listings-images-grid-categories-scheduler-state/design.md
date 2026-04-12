# Design: Listings images/grid, query category selection, and scheduler reconciliation

## Summary

This change is primarily a focused UX enhancement with one backend integration addition and one scheduler correctness fix.

## Listings UI

- Keep the query-group accordion structure already added to the Listings page.
- Add a page-level `viewMode` state with `list` and `grid` options.
- Extend the listings renderer so both modes use the same paginated data source.
- In list mode:
  - Show a thumbnail at the start of each row.
  - Keep the denser metadata columns for price, type, state, and last seen.
- In grid mode:
  - Render responsive cards with image, title, price, and compact metadata.
  - Preserve the same eBay outbound link behavior.
- Use the search query (`keyword`) as the primary label in query group headers so the UI no longer depends on a separate custom name.

## Query creator/editor

- Remove the visible `name` input from the frontend form.
- Keep backend storage compatibility by deriving `name` from `keyword` whenever the client omits `name`.
- Add a lightweight config endpoint that returns category suggestions for a given `site_id` and search string.
- Use the selected marketplace plus the deferred search query value to fetch suggestions only when there is enough input to be meaningful.
- Store the selected `category_id` on the query record; the UI will show a neutral "All categories" option when nothing is selected.

## eBay category suggestions

- Add a backend taxonomy service that:
  - Reuses the existing OAuth client-credentials flow.
  - Looks up the default category tree for the marketplace.
  - Requests keyword-based suggestions from `getCategorySuggestions`.
- Return a frontend-friendly shape with:
  - `category_id`
  - `category_name`
  - `category_path` assembled from ancestor names plus the leaf category name
- Keep the endpoint read-only and stateless; the frontend will request suggestions on demand.

## Scheduler lifecycle and status

- Replace the current status logic that treats `not paused` as `running`.
- Maintain real scheduler lifecycle helpers around APScheduler's async context manager and background runner.
- Add a reconciliation layer that:
  - Starts the scheduler in the background only when at least one enabled query exists.
  - Adds or replaces a schedule when an enabled query is created or updated.
  - Removes a schedule when a query is disabled or deleted.
  - Stops the scheduler when no schedules remain.
- Implement pause/resume by pausing and unpausing concrete schedules, using `resume_from="now"` to avoid stale misfires after resume.
- Expose status based on actual running poll jobs, with separate counts for scheduled queries waiting to run.

## API surface changes

- `GET /api/v1/config/ebay-category-suggestions?site_id=...&q=...`
  - Returns category suggestions for the current marketplace and search text.
- Query create/update behavior:
  - `name` becomes optional from the client's perspective.
  - If omitted, backend derives it from `keyword`.

## Verification plan

- Backend tests:
  - Category suggestion endpoint response/validation behavior.
  - Query create/update deriving `name` from `keyword`.
  - Scheduler status returning idle while scheduled queries are waiting, and only returning running when a poll job is actively executing.
- Frontend verification:
  - Query form shows search query and category selector without a separate name field.
  - Listings page shows thumbnails in list mode and cards in grid mode.
  - Scheduler page shows idle when queries are waiting for their next run.
