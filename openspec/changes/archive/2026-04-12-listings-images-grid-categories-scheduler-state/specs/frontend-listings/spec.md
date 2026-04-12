# Frontend listings enhancements

## ADDED Requirements

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
