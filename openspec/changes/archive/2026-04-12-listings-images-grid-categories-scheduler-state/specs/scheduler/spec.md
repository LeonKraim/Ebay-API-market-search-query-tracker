# Scheduler active-state reconciliation

## ADDED Requirements

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
