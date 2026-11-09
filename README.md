# Project Memory MCP Server

A FastMCP server for storing and retrieving project context using PostgreSQL.

## Technology Stack

- Python 3.13
- FastMCP 4.x
- SQLAlchemy 2.x and Psycopg 3
- PostgreSQL (including Neon)
- Pydantic Settings

## Setup

Install dependencies and create a local environment file:

```bash
uv sync
cp .env.example .env
```

Set `DATABASE_URL` in `.env`. For local development, keep `APP_ENV=development`;
authentication is disabled only in that explicitly selected environment. All
other environments require `AUTH_TOKEN`. Do not expose a development server to
the public internet.

## Run the Server

```bash
uv run project-memory-mcp-live
```

Alternatively:

```bash
uv run python -m project_memory_mcp_live.server
```

## Database Migrations

Apply migrations manually when running outside the container:

```bash
uv run alembic upgrade head
```

The Docker image applies migrations before starting the server. Configure
`DATABASE_URL` and `AUTH_TOKEN` in the deployment environment. The container
binds to `0.0.0.0` and uses the deployment-provided `PORT` when available.

## Tests

Set `TEST_DATABASE_URL` to a dedicated test database before running the suite.
The test setup refuses to use the configured production database URL.

```bash
uv run pytest -v
```

## Project Status

The server currently supports project, task, decision, and project-update
workflows, with PostgreSQL persistence and bearer-token authentication outside
explicit local development.
