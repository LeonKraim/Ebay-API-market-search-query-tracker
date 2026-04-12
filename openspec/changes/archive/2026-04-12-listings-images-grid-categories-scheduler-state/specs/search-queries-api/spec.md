# Search queries API enhancements

## ADDED Requirements

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
