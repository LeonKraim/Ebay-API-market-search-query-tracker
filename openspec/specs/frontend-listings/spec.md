# frontend-listings Specification

## Purpose
TBD - created by archiving change listings-query-groups-and-stats-fix. Update Purpose after archive.
## Requirements
### Requirement: Query group accordion expansion
- The Listings page MUST group all listings by query name
- Each query MUST be a collapsible card; click to expand and load listings
- Expanded group MUST show listing count badge

#### Scenario: User expands a query group
- User clicks query group header
- Listings load with query_id filter (25 per page)
- Group shows chevron icon state (▶ collapsed, ▼ expanded)
- Pagination controls appear within expanded section

### Requirement: Listing title links
- Listing titles MUST be blue clickable links to eBay items
- Links MUST open in new tab with proper security attributes
- No separate Link column MUST exist

#### Scenario: User clicks a listing title
- User clicks blue title text on a listing row
- Browser opens the eBay item URL in a new tab
- Existing page is not navigated away from

### Requirement: UseListings enabled option
- Hook MUST accept `{ enabled?: boolean }` option to defer fetching

#### Scenario: Query is conditionally enabled
- When `enabled=false`, query does not fetch
- When `enabled` switches to `true`, query fetches immediately

### Requirement: Listings show thumbnails in list view
- The Listings page MUST show a thumbnail image for each listing when rendered in list view.
- When no image is available, the UI MUST show a stable placeholder instead of a broken image.

#### Scenario: User expands a query group in list view
- Given a query group contains listing records
- When the user expands the group while list view is selected
- Then each listing row shows a thumbnail beside the title
- And each title remains a clickable link to the eBay item

### Requirement: Listings support rasterized grid view
- The Listings page MUST provide a toggle between list view and rasterized grid view.
- Grid view MUST render each listing as an image-first card with compact metadata.

#### Scenario: User switches to grid view
- Given a query group is expanded and has listings
- When the user selects grid view
- Then the listings render as cards in a responsive grid
- And each card shows image, title, price, and key metadata

### Requirement: Query groups use the search query as the primary label
- Listings query group headers MUST use the search query text as the primary visible label.

#### Scenario: User views grouped listings
- Given a saved query with a keyword and stored record
- When the Listings page renders the accordion groups
- Then the header prominently shows the query keyword as the group label

### Requirement: Query groups support direct navigation
- The market browser MUST support opening directly to a selected query's live listings from other query surfaces in the app.

#### Scenario: User clicks a query card
- Given the user is viewing a query surface such as Dashboard or Queries
- When the user clicks a query card or recent-query row
- Then the app navigates to the market browser
- And the market mode is `live`
- And the selected query group is expanded automatically

### Requirement: Listings and sold browsing share one top-level destination
- The app MUST expose one top-level market-browsing destination instead of separate sidebar destinations for listings and sold records.
- The market page MUST let users switch between live listings and sold records without leaving the page.

#### Scenario: User switches between live and sold data
- Given the user is on the market page
- When the user selects the sold mode
- Then sold records are shown in the content area
- And the sidebar selection remains on the single market destination

