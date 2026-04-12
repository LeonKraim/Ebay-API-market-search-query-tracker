# Scheduler Capability

## ADDED Requirements

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
