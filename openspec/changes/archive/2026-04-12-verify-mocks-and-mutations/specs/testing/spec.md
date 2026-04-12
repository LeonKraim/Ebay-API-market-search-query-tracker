# Testing Capability

## ADDED Requirements

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
