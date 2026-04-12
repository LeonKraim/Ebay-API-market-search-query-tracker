# Search Queries API Capability

## ADDED Requirements

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
