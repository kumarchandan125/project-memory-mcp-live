
# Project Memory MCP Server

A personal project-memory application powered by FastMCP
and Neon PostgreSQL.

## Technology Stack

- Python 3.13
- FastMCP 4.x
- SQLAlchemy 2.x
- Psycopg 3
- Neon PostgreSQL
- Pydantic Settings

## Setup

Install dependencies:

```bash
uv sync
```

Configure environment variables:

```bash
cp .env.example .env
```

Add your Neon PostgreSQL connection URL to `.env`.

## Run the Server

```bash
uv run python -m project_memory_mcp.server
```

## Run Tests

```bash
uv run pytest -v
```

## Project Status

Phase 1: Project Foundation
