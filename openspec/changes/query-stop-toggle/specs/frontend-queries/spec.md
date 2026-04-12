# Queries page inline poll controls

## ADDED Requirements

### Requirement: Query cards expose inline poll control
- The Queries page MUST show a stop control on a query card while that query is actively polling.

#### Scenario: Query is actively polling
- Given a query is included in the scheduler status `running_query_ids`
- When the Queries page renders that query card
- Then the card shows a `Stop` action instead of `Run now`

#### Scenario: Query is idle
- Given a query is not included in the scheduler status `running_query_ids`
- When the Queries page renders that query card
- Then the card shows `Run now`

### Requirement: Query cards expose inline enabled toggle
- The Queries page MUST let the user enable or disable a query directly from its status badge.

#### Scenario: Disable a query from its card
- Given a query card is currently enabled
- When the user clicks its enabled badge
- Then the page sends an update that sets `enabled=false`

#### Scenario: Enable a query from its card
- Given a query card is currently disabled
- When the user clicks its disabled badge
- Then the page sends an update that sets `enabled=true`