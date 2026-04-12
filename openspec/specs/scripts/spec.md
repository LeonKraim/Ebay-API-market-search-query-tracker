# scripts Specification

## Purpose
TBD - created by archiving change start-and-clear-scripts. Update Purpose after archive.
## Requirements
### Requirement: Start the full stack with a single command
The system MUST provide a `start.bat` that builds and starts all Docker services.

#### Scenario: Docker not installed
- Given `docker` is not on PATH
- Then the script MUST print an error message and exit non-zero

#### Scenario: Missing .env file
- Given `.env` does not exist
- Then the script MUST copy `.env.example` to `.env` and instruct the user to edit it before proceeding

#### Scenario: Happy path startup
- Given Docker is available and `.env` exists
- When the user runs `start.bat`
- Then all services start in detached mode and the frontend URL is printed

### Requirement: Clear all persisted data with a single command
The system MUST provide a `clear_data.bat` that wipes all volumes and logs after confirmation.

#### Scenario: User declines confirmation
- Given the user answers `n` at the confirmation prompt
- Then no data is deleted and the script exits cleanly

#### Scenario: User confirms deletion
- Given the user answers `y` at the confirmation prompt
- Then `docker compose down -v` MUST run and log files MUST be deleted

