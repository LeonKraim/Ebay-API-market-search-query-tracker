## ADDED Requirements

### Requirement: Sidebar shows destinations without the top wordmark
- The sidebar MUST prioritize navigation destinations and status content without rendering a standalone top-left product wordmark.

#### Scenario: User views the app shell
- Given the user has loaded the app
- When the sidebar renders
- Then the top-left wordmark is absent
- And the navigation destinations remain visible and usable

### Requirement: Sidebar footer credit is shown
- The sidebar MUST show a footer credit reading `made by leon kraim` in the lower left area.

#### Scenario: User views the sidebar footer
- Given the sidebar is visible
- When the user looks at the lower left footer area
- Then the text `made by leon kraim` is shown