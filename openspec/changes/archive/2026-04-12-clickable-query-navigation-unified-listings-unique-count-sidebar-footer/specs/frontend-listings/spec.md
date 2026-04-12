## ADDED Requirements

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