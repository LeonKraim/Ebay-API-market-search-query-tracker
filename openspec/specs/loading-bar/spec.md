# loading-bar Specification

## Purpose
TBD - created by archiving change remove-loading-bar. Update Purpose after archive.
## Requirements
### Requirement: No top loading bar in the frontend
- The frontend MUST NOT display a top progress/loading bar during API requests.

#### Scenario: No loading bar during API request
- Given the user triggers any API request (page load, data fetch, etc.)
- When the request is in flight
- Then no blue progress bar appears at the top of the viewport

#### Scenario: No NProgress CSS present
- Given the frontend CSS is loaded
- When the DOM is inspected
- Then no `#nprogress` styles are applied

