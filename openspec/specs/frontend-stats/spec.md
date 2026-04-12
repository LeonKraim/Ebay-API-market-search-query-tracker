# frontend-stats Specification

## Purpose
TBD - created by archiving change listings-query-groups-and-stats-fix. Update Purpose after archive.
## Requirements
### Requirement: Tooltip null guard and number formatting
- Tooltip formatter MUST correctly handle numeric values and null values
- Values MUST render as "£X.XX" format or "—" for null
- No TypeError crashes MUST occur when hovering

#### Scenario: User hovers over a chart data point
- Tooltip displays with date label formatted as "D MMM YYYY"
- Each price line renders as "£82.58" (formatted) or "—" for null
- No crash occurs; Recharts tooltip renders smoothly

### Requirement: X-axis date label formatting
- Date labels on X-axis MUST render as "D MMM" (e.g., "6 Apr")
- Dates MUST be readable and properly spaced

#### Scenario: Chart renders with data
- X-axis labels show formatted dates not ISO strings
- All dates visible; no blank or malformed values

### Requirement: PriceTrendPoint type alignment
- Interface MUST use `date` field not `period` to match backend
- Backend sends `date: datetime`; frontend MUST expect `date: string`

#### Scenario: API response deserializes correctly
- Chart data keys match expected field names
- No data loss due to field name mismatches

