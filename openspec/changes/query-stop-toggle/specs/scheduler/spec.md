# Scheduler active query reporting

## ADDED Requirements

### Requirement: Scheduler status exposes active query IDs
- The scheduler status endpoint MUST expose the IDs of queries whose poll jobs are currently active.

#### Scenario: Polls are currently running
- Given queries `12` and `18` are actively polling
- When GET `/api/v1/scheduler/status` is called
- Then the response is HTTP 200
- And `running_query_ids` contains `12` and `18`

#### Scenario: No polls are currently running
- Given no query polls are currently active
- When GET `/api/v1/scheduler/status` is called
- Then the response is HTTP 200
- And `running_query_ids` is an empty list