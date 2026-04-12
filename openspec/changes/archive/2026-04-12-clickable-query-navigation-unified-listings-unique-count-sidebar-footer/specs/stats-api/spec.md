## ADDED Requirements

### Requirement: Items evaluated counts unique items
- The `GET /api/v1/stats/items-evaluated` endpoint MUST report the number of unique non-null item IDs across live listings and sold records.
- Duplicate appearances of the same item ID across snapshots or across live/sold tables MUST only contribute once to the total.

#### Scenario: Same item appears in multiple sources
- Given a live listing item ID appears in multiple listing rows and also appears in sold records
- When GET `/api/v1/stats/items-evaluated` is called
- Then the response counts that item ID only once in `total`

### Requirement: Items evaluated since timestamp uses the earliest observation
- The `since` field returned by `GET /api/v1/stats/items-evaluated` MUST reflect the earliest available observation timestamp across live and sold sources.

#### Scenario: Sold data exists before live data
- Given the earliest sold observation predates the earliest live observation
- When GET `/api/v1/stats/items-evaluated` is called
- Then the response `since` equals the earliest sold observation timestamp