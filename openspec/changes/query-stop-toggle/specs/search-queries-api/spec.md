# Query stop endpoint and guarded deletion

## ADDED Requirements

### Requirement: Stop an active query poll
- The system MUST allow a client to request that an active query poll stop.

#### Scenario: Stop an active query poll
- Given query `123` currently has an active poll
- When POST `/api/v1/queries/123/stop` is called
- Then the response is HTTP 200
- And the response confirms that stop was requested for query `123`

#### Scenario: Stop request for idle query
- Given query `123` does not currently have an active poll
- When POST `/api/v1/queries/123/stop` is called
- Then the response is HTTP 404

### Requirement: Deleting an actively polling query requires stopping it first
- The system MUST reject deletion of a query that is actively polling and tell the client to stop the poll first.

#### Scenario: Delete active query
- Given query `123` currently has an active poll
- When DELETE `/api/v1/queries/123` is called
- Then the response is HTTP 409
- And the error message instructs the client to stop the poll first