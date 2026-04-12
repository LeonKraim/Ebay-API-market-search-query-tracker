# testing Specification

## Purpose
TBD - created by archiving change mock-data-ebay-tests. Update Purpose after archive.
## Requirements
### Requirement: Mock eBay Finding API tests
The test suite MUST include unit tests for `fetch_all_listings` and `_fetch_page` that mock the HTTP transport and verify pagination, retry, and error handling without calling the real eBay API.

#### Scenario: Single page fetch returns parsed listings
Given a mock httpx response containing valid Finding API XML with 3 items on 1 page
When `fetch_all_listings` is called
Then it MUST return 3 `RawListing` objects with correct fields

#### Scenario: Multi-page pagination
Given mock responses for page 1 (totalPages=2) and page 2
When `fetch_all_listings` is called
Then it MUST fetch both pages and return 5 total listings

#### Scenario: Retry on HTTP 429
Given a mock that returns 429 once then succeeds
When `_fetch_page` is called
Then it MUST retry and return the listings from the successful response

#### Scenario: Non-retryable HTTP error
Given a mock that returns HTTP 403
When `fetch_all_listings` is called
Then it MUST raise an `httpx.HTTPStatusError`

### Requirement: Mock sold scraper tests
The test suite MUST include unit tests for `scrape_sold_listings` and `_parse_page` that mock the HTTP transport and verify HTML parsing, pagination, and config gating.

#### Scenario: Parse sold items from HTML
Given a mock httpx response containing realistic eBay sold listings HTML with 3 items
When `scrape_sold_listings` is called
Then it MUST return 3 `RawSoldItem` objects with correct fields

#### Scenario: Scraper disabled
Given settings with `scraper_enabled = False`
When `scrape_sold_listings` is called
Then it MUST return an empty list without making HTTP calls

### Requirement: Mock poll runner tests
The test suite MUST include unit tests for `run_poll` that mock both eBay API calls and the database session, verifying the orchestration logic.

#### Scenario: Happy path poll
Given a mocked `fetch_all_listings` returning 2 listings and a mocked DB session
When `run_poll` is called for an enabled query
Then it MUST create a snapshot, insert listing records, and mark the snapshot complete

#### Scenario: Concurrent job guard
Given a query ID already in `_running_jobs`
When `run_poll` is called for the same query ID
Then it MUST skip execution and return without error

### Requirement: Mock fixtures validated against real eBay API
Test fixture XML and HTML MUST be structurally validated against real eBay API responses to ensure namespaces, element names, CSS selectors, and data shapes match production.

#### Scenario: Finding API XML structure matches
Given a real eBay Finding API XML response
When compared against fixture XML files
Then the namespace URI, root element, searchResult/item child elements, and paginationOutput structure MUST match

#### Scenario: Sold page HTML structure matches
Given a real eBay completed/sold listings HTML page
When compared against fixture HTML files
Then the CSS selectors used by `_parse_page` (li.s-item, .s-item__title, .s-item__price, .s-item__ended-date, .s-item__link, .s-item__image-img, .pagination__next) MUST match elements found in the real page

