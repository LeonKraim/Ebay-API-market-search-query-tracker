# Config category suggestion endpoint

## ADDED Requirements

### Requirement: eBay category suggestions endpoint
- The system MUST expose a read-only endpoint that returns marketplace-aware eBay category suggestions for a search string.

#### Scenario: Request category suggestions for a marketplace
- Given a valid `site_id` and non-empty query string `q`
- When GET `/api/v1/config/ebay-category-suggestions` is called
- Then the response includes zero or more suggested categories with IDs and human-readable names/paths

#### Scenario: Request suggestions with blank query text
- Given `q` is blank or whitespace only
- When GET `/api/v1/config/ebay-category-suggestions` is called
- Then the response returns an empty suggestion list without calling eBay suggestion lookup
