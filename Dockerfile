FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY . .
RUN uv sync --frozen --no-dev --no-cache

CMD uv run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
