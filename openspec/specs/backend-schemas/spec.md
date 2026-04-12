# backend-schemas Specification

## Purpose
TBD - created by archiving change listings-query-groups-and-stats-fix. Update Purpose after archive.
## Requirements
### Requirement: Float serialization for price fields
- Price fields in stats schemas MUST use `float | None` (not `Decimal`)
- JSON response MUST contain numeric values not string representations

#### Scenario: API returns price trend data
- PriceTrendPoint: avg_price, min_price, max_price are `float | None`
- SoldTrendPoint: avg_price, min_price, max_price are `float | None`
- QuerySummary: all avg_* and price_delta are `float | None`
- Frontend receives `215.50` not `"215.50"`

### Requirement: Granularity parameter naming
- Stats endpoints MUST use `granularity` query param (not `interval`)
- Parameter MUST be correctly passed to SQL truncation function

#### Scenario: Frontend calls stats endpoint with granularity
- URL: `/stats/price-trend?granularity=week`
- Backend receives and uses granularity param
- No silent defaults occur from parameter mismatches

