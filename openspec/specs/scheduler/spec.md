# scheduler Specification

## Purpose
TBD - created by archiving change ebay-market-intel-platform. Update Purpose after archive.
## Requirements
### Requirement: Scheduler status endpoint
The system MUST expose the scheduler's running/paused state.

#### Scenario: Get status when running
- Given the scheduler is running
- When GET /api/v1/scheduler/status is called
- Then the API returns HTTP 200 with {"running": true, "paused": false}

#### Scenario: Get status when paused
- Given the scheduler has been paused
- When GET /api/v1/scheduler/status is called
- Then the API returns HTTP 200 with {"paused": true}

### Requirement: Pause and resume scheduler
The system MUST allow pausing and resuming all scheduled jobs.

#### Scenario: Pause scheduler
- Given the scheduler is running
- When POST /api/v1/scheduler/pause is called
- Then the API returns HTTP 200 and all pending jobs are paused

#### Scenario: Resume scheduler
- Given the scheduler is paused
- When POST /api/v1/scheduler/resume is called
- Then the API returns HTTP 200 and jobs resume executing

### Requirement: Run all queries immediately
The system MUST allow triggering all enabled queries to run now regardless of schedule.

#### Scenario: Run all now
- Given at least one enabled query exists
- When POST /api/v1/scheduler/run-all is called
- Then the API returns HTTP 200 and each enabled query's poll job is enqueued immediately

### Requirement: Scheduler running state reflects active poll execution
- The scheduler status endpoint MUST report `running=true` only when at least one poll job is actively executing.
- The scheduler status endpoint MUST expose scheduled query counts separately so the UI can show `idle` while work is waiting for the next run.

#### Scenario: No enabled queries exist
- Given there are no enabled queries with schedules
- When GET `/api/v1/scheduler/status` is called
- Then the response is HTTP 200 with `running=false`
- And `paused=false`
- And `active_schedules=0`

#### Scenario: Enabled queries exist but no poll job is currently executing
- Given at least one enabled query has an active schedule
- And no poll job is currently executing
- When GET `/api/v1/scheduler/status` is called
- Then the response is HTTP 200 with `running=false`
- And `active_schedules` is greater than 0

### Requirement: Query CRUD reconciles scheduler schedules
- The system MUST reconcile background schedules when queries are created, updated, disabled, enabled, or deleted.

#### Scenario: Create enabled query
- Given no schedules currently exist
- When an enabled query is created
- Then a schedule is added for that query
- And the scheduler becomes idle until the next poll task starts

#### Scenario: Disable or delete the last enabled query
- Given exactly one enabled query schedule exists
- When that query is disabled or deleted
- Then its schedule is removed
- And the scheduler becomes idle

