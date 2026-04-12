# ebay-integration Specification

## Purpose
TBD - created by archiving change ebay-market-intel-platform. Update Purpose after archive.
## Requirements
### Requirement: Fetch active listings via Finding API
The system MUST query the eBay Finding API to retrieve active listings for a keyword.

#### Scenario: Successful fetch returns RawListing list
- Given a valid eBay App ID in config and a keyword "nintendo switch"
- When the finding service fetches page 1
- Then a list of RawListing dataclass instances is returned with item_id, current_price as Decimal, currency, and item_url populated

#### Scenario: Price is stored as Decimal not float
- Given a listing with price "249.99" in the XML response
- When _parse_listing() processes the item
- Then current_price equals Decimal("249.99") to avoid floating-point precision errors

### Requirement: Deduplication against existing listings
The system MUST classify fetched listings into new / updated / unchanged buckets.

#### Scenario: New item not in database
- Given an item_id that has never been seen before
- When classify() is called with that item against an empty existing dict
- Then the item appears in the new bucket

#### Scenario: Unchanged when price matches
- Given an existing item with price Decimal("9.99")
- When classify() is called with the same item at the same price
- Then the item appears in the unchanged bucket and not in new or updated

#### Scenario: Updated when price changes
- Given an existing item with price Decimal("9.99")
- When classify() receives the same item at price Decimal("7.50")
- Then the item appears in the updated bucket

### Requirement: Global configuration endpoint
The system MUST expose non-secret configuration values via GET /api/v1/config.

#### Scenario: Config excludes secrets
- Given credentials are stored in environment variables
- When GET /api/v1/config is called
- Then the response body does not contain API keys, database passwords, or auth tokens

#### Scenario: Config contains app metadata
- Given the system is running
- When GET /api/v1/config is called
- Then the response contains an "app" section with at least a "title" key

