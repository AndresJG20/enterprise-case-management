# CaseFlow — Enterprise Case Management

![CI](https://github.com/AndresJG20/enterprise-case-management/actions/workflows/ci.yml/badge.svg)

Portfolio application for generic case management. Synthetic demonstration only; no institutional data.

## Features
Authenticated sessions, administrator/analyst roles, scoped access, registration and assignment, search and pagination, guarded state transitions, optimistic locking, audit history and metrics. Responsive browser UI; REST API with OpenAPI. SQLite for development and PostgreSQL configuration via Docker Compose.

## Run locally
Python 3.12. Create and activate a virtual environment, install dependencies, set CASEFLOW_ADMIN_PASSWORD to a unique password of at least 12 characters (PowerShell: $env:CASEFLOW_ADMIN_PASSWORD = "your-local-password"), then:
```bash
pip install -r requirements-dev.txt
python -m backend.seed
python -m uvicorn backend.main:app
```
Open http://localhost:8000, login as admin. Use /docs to create analysts and explore the API. Administrator password is not stored in source.

## PostgreSQL
Copy .env.example to .env and set unique local values (use URL-safe database password). Run docker compose up -d --build, then docker compose exec app python -m backend.seed. Use a fresh database; the initial prototype database is not migrated.

## Testing
```bash
python -m pytest -q
```
CI runs integration tests against a temporary SQLite database and builds the image. PostgreSQL integration and browser E2E are not yet verified.

## Structure
- backend/: configuration, models, schemas, repositories, services, security, API
- frontend/: HTML, CSS, JavaScript
- tests/: API integration
- docs/: architecture and limitations

See [architecture](docs/architecture.md). No production claims: add TLS, rate limiting, migrations and security review before exposing the application.
