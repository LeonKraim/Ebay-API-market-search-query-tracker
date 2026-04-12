# Proposal: Listings images, grid view, category selector, and scheduler state fix

## What Changes

Implement four related improvements across the frontend and backend:

1. Add listing thumbnails to the Listings tab and provide a toggle between the existing list/table presentation and a rasterized grid/card view.
2. Update the query creator/editor so the tracked search is identified by its search query rather than a separate custom name field.
3. Add category selection to the query creator/editor by sourcing category suggestions from eBay for the selected marketplace and search query.
4. Fix scheduler lifecycle and status reporting so scheduled queries are reconciled correctly, while the UI reports `running` only when a poll task is actively executing and `idle` when queries are merely waiting for the next scheduled run.

## Why

- Listings are image-heavy e-commerce results; users need visual scanning in addition to the denser row-based view.
- The separate query name field adds duplicate input with little value for this product; the search query itself should be the primary label.
- Category filtering already exists in the data model and eBay fetch layer, but users cannot currently select it from the UI.
- The scheduler UI is misleading today because it reports "running" even when no poll task is actively executing, and the backend does not reliably reconcile schedule state with query CRUD operations.

## Referenced best-practice sources

- Material Design 3 Cards and Grid Lists guidance: image-first collections should use cards/grid tiles with consistent primary actions and truncated text to preserve scan rhythm.
  - https://m3.material.io/components/cards
  - https://m1.material.io/components/grid-lists.html
- eBay Taxonomy API overview and category suggestion flow: get the marketplace's default category tree, then request keyword-based category suggestions for selection.
  - https://developer.ebay.com/api-docs/commerce/taxonomy/overview.html
  - https://developer.ebay.com/api-docs/commerce/taxonomy/resources/category_tree/methods/getDefaultCategoryTreeId
  - https://developer.ebay.com/api-docs/commerce/taxonomy/resources/category_tree/methods/getCategorySuggestions
- APScheduler async lifecycle guidance: initialize the scheduler as a context manager, start it in the background, and pause/unpause/remove concrete schedules rather than inferring running state from an unrelated flag.
  - https://apscheduler.readthedocs.io/en/master/userguide.html

## Acceptance criteria

1. On the Listings tab, each listing row shows a thumbnail image beside the title, or a clear placeholder when no image is available.
2. On the Listings tab, users can switch between list and rasterized grid views without leaving the page, and both views work inside each query accordion group.
3. In the query creator/editor, users only enter a search query, not a separate custom name, and the UI uses that search query as the visible query label.
4. In the query creator/editor, users can select an optional eBay item category suggested for the current search query and marketplace.
5. On the Scheduler tab, when queries are scheduled but no poll task is actively executing, the scheduler is shown as `idle` and the UI indicates how many queries are waiting for the next run.
6. When a poll task is actively executing, the scheduler is shown as `running`; when the last enabled query is disabled or deleted, the scheduler returns to idle with zero scheduled queries.
