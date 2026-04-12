# Frontend: Listings Page Redesign

## ADDED Requirements

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

