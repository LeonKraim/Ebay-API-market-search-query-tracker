# config Specification

## Purpose
TBD - created by archiving change fix-docker-db-config. Update Purpose after archive.
## Requirements
### Requirement: Database env var override
The `get_settings()` function MUST apply environment variable overrides for `DATABASE_HOST`, `DATABASE_PORT`, and `DATABASE_NAME` after loading config.toml, so that Docker runtime env vars take precedence.

#### Scenario: Docker environment provides DATABASE_HOST
Given the environment variable `DATABASE_HOST` is set to `postgres`
When `get_settings()` is called
Then `settings.db_host` MUST equal `postgres`

#### Scenario: No DATABASE_HOST in environment
Given the environment variable `DATABASE_HOST` is not set
When `get_settings()` is called
Then `settings.db_host` MUST equal the value from config.toml (default `localhost`)

#### Scenario: Docker environment provides DATABASE_NAME
Given the environment variable `DATABASE_NAME` is set to `ebay_market_intel`
When `get_settings()` is called
Then `settings.db_name` MUST equal `ebay_market_intel`

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

