# search-queries-api Specification

## Purpose
TBD - created by archiving change ebay-market-intel-platform. Update Purpose after archive.
## Requirements
### Requirement: Create search query
The system MUST allow creating a new tracked search query via POST /api/v1/queries.

#### Scenario: Create valid query
- Given a POST request to /api/v1/queries with keyword and name
- When the request body passes schema validation
- Then the API returns HTTP 201 with the created query object including a numeric id

#### Scenario: Reject blank keyword
- Given a POST request with keyword containing only whitespace
- When the validator runs
- Then the API returns HTTP 422 with validation error details

#### Scenario: Reject missing keyword
- Given a POST request with no keyword field
- When the validator runs
- Then the API returns HTTP 422

### Requirement: Retrieve search query by ID
The system MUST retrieve a single query by its integer ID.

#### Scenario: Get existing query
- Given a query with id=1 exists in the database
- When GET /api/v1/queries/1 is called
- Then the API returns HTTP 200 with the full query object

#### Scenario: Not found
- Given no query with id=9999 exists
- When GET /api/v1/queries/9999 is called
- Then the API returns HTTP 404

### Requirement: List search queries with pagination
The system MUST list all queries with page/page_size pagination.

#### Scenario: Empty list
- Given no queries exist
- When GET /api/v1/queries is called
- Then the API returns HTTP 200 with items=[] and total=0

#### Scenario: Reject page_size=0
- Given a request with page_size=0
- When query validation runs
- Then the API returns HTTP 422

### Requirement: Update search query
The system MUST support partial update (PATCH) of a query.

#### Scenario: Update name
- Given a query exists
- When PATCH /api/v1/queries/{id} is called with {"name": "New Name"}
- Then the API returns HTTP 200 with name updated to "New Name"

#### Scenario: Empty body is no-op
- Given a query exists
- When PATCH with an empty body {} is called
- Then the API returns HTTP 200 with the original query unchanged

### Requirement: Delete search query
The system MUST support deleting a query and its related data.

#### Scenario: Delete existing query
- Given a query with id=1 exists
- When DELETE /api/v1/queries/1 is called
- Then the API returns HTTP 204 and the query is no longer retrievable

### Requirement: Query label can be derived from the search query
- The system MUST allow query creation without a separately supplied custom name.
- When `name` is omitted, the backend MUST derive the stored label from `keyword`.

#### Scenario: Create query without a custom name
- Given a POST request to `/api/v1/queries` with `keyword` and no `name`
- When the request is accepted
- Then the created query stores and returns `name` equal to the `keyword`

#### Scenario: Update keyword without sending a custom name
- Given an existing query whose label should mirror the search query
- When PATCH `/api/v1/queries/{id}` updates only `keyword`
- Then the returned query stores and returns `name` equal to the updated `keyword`

### Requirement: Queries preserve optional category selection
- The system MUST persist an optional `category_id` across query create and update operations.

#### Scenario: Create query with category filter
- Given a POST request includes `category_id`
- When the query is created
- Then the response includes the same `category_id`

#### Scenario: Remove category filter
- Given an existing query with a category filter
- When PATCH `/api/v1/queries/{id}` sets `category_id` to null
- Then the response shows `category_id` as null

