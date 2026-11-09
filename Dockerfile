
FROM python:3.13-slim

# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Python and uv configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy dependency files first
COPY pyproject.toml uv.lock README.md ./

# Copy application source and migrations
COPY src ./src
COPY migrations ./migrations
COPY alembic.ini ./

# Install production dependencies using the lockfile
RUN uv sync --frozen --no-dev

# Railway will provide the PORT environment variable
EXPOSE 8000

# Start the FastMCP server
CMD ["uv", "run", "--no-sync", "python", "-m", "project_memory_mcp_live.server"]
