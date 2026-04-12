# Design: Stop active polls and inline query enable toggle

## Approach
Use cooperative cancellation instead of forcefully cancelling the poll task. The poll runner tracks a per-query `asyncio.Event` keyed by query id. The stop endpoint sets the event, `fetch_all_listings()` checks it between page requests so paging stops after the current in-flight request, and `run_poll` checks it again before writing fetched results. This avoids spreading `CancelledError` handling through the polling stack while still letting the user stop active work during an active fetch.

On the frontend, the Queries page combines local `Run now` pending state with scheduler-reported `running_query_ids` so each card can reliably render its current action. Mutations invalidate the query list and scheduler status keys to resync UI state.

## Backend Changes

### 1. Poll runner stop signal
- Add `_cancel_events: dict[int, asyncio.Event]`
- Register an event when a query starts polling
- Expose `cancel_poll(query_id)` to set the event when the query is active
- Expose `get_running_query_ids()` for scheduler status reporting
- Pass the cancellation predicate into `fetch_all_listings()` so page-fetching stops before the next page request
- Check `cancel_event.is_set()` after the eBay fetch and before persisting fetched results
- Mark the snapshot as `cancelled` with a user-facing error message when a stop request wins the race

### 2. Query router stop endpoint
- Add `POST /api/v1/queries/{id}/stop`
- Return `404` when no active poll exists for that query
- Return a confirmation payload when stop was requested
- Keep delete protection in place, but point the user to the stop control first

### 3. Scheduler status expansion
- Extend `get_scheduler_status()` to include `running_query_ids`
- Extend the scheduler router response model to include `running_query_ids: list[int]`

## Frontend Changes

### 4. API client and hooks
- Extend `SchedulerStatus` with `running_query_ids`
- Add `api.queries.stop(id)`
- Add `useStopQueryPoll()` mutation that invalidates scheduler status and query list data
- Shorten scheduler status polling cadence so stop state clears promptly in the UI

### 5. Query card controls
- Render the enabled badge as a clickable control that toggles `query.enabled`
- Show `Stop` when the query is actively polling
- Show `Run now` when the query is idle

### 6. Queries page wiring
- Consume scheduler status so polling state comes from the backend, not only local optimistic state
- Add `handleStopPoll` and `handleToggleEnabled`
- Preserve existing edit, run, and delete actions

## Tradeoffs
- Cooperative cancellation does not interrupt the network request mid-flight. It stops the poll at the next safe checkpoint, which is simpler and safer than injecting `CancelledError` through the whole polling stack.
- Scheduler status polling remains periodic instead of websocket-driven. This keeps the change small and aligned with the current polling architecture.