# Proposal: Stop active polls and toggle query enabled state from query cards

## What
Add inline controls on the Queries page so each query card can:

1. Stop an actively running poll without waiting for the full fetch cycle to finish
2. Toggle the query's enabled or disabled state directly from the card
3. Surface active polling state from the scheduler so the UI can show which specific queries are currently running

The backend will expose a `POST /api/v1/queries/{id}/stop` endpoint and extend scheduler status to include `running_query_ids`.

## Why
The current delete protection prevents deleting a query while a poll is in progress, but it leaves the user without the missing control they actually need: stop the in-flight poll first, then delete. The user also expects the enabled state to be manageable directly on the Queries page instead of opening the edit form.

This change restores the expected workflow:

- user sees which query is actively polling
- user can stop that poll from the same card
- user can then delete the query if needed
- user can enable or disable a query inline from the card

## Acceptance Criteria
1. When a query is actively polling, its card shows a `Stop` action instead of `Run now`.
2. Clicking `Stop` sends a stop request, the current poll is cancelled at a safe checkpoint, and the query no longer appears in the active polling set.
3. When a query is not actively polling, its card shows `Run now`.
4. Clicking the enabled badge on a query card toggles the query's enabled state without opening the edit form.
5. Attempting to delete an actively polling query returns a clear message instructing the user to stop it first.

## Best Practice Sources
1. Python asyncio task cancellation docs: `Task.cancel()` raises `CancelledError` at the next await opportunity and cleanup should use `try/finally`, which supports using cooperative checkpoints for safe shutdowns. https://docs.python.org/3/library/asyncio-task.html#task-cancellation
2. Python asyncio synchronization docs: `asyncio.Event` is the standard primitive for signalling state changes between asyncio tasks, with `is_set()` and `set()` semantics that fit cooperative cancellation flags. https://docs.python.org/3/library/asyncio-sync.html#event
3. TanStack Query invalidation docs: mutation handlers should invalidate related query keys so active views refetch and stay in sync after a state-changing action. https://tanstack.com/query/latest/docs/framework/react/guides/query-invalidation and https://tanstack.com/query/latest/docs/framework/react/guides/invalidations-from-mutations

## Scope
- Backend poll runner: cooperative stop signal and cleanup state
- Backend query router: stop endpoint and delete guidance
- Backend scheduler status: expose `running_query_ids`
- Frontend API client and hooks: stop mutation and refreshed scheduler status
- Queries page and query card: stop button and inline enabled toggle