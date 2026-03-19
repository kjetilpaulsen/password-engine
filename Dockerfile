# syntax=docker/dockerfile:1.7

FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

# Copy dependency metadata first for better layer caching
COPY pyproject.toml uv.lock ./

# Install runtime dependencies into /opt/venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy application source
COPY src ./src
COPY README.md ./

# Install the project itself into the venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    XDG_DATA_HOME=/xdg/data \
    XDG_STATE_HOME=/xdg/state \
    XDG_CACHE_HOME=/xdg/cache \
    XDG_CONFIG_HOME=/xdg/config

WORKDIR /app

RUN useradd --create-home --uid 10001 appuser && \
    mkdir -p /xdg/data /xdg/state /xdg/cache /xdg/config && \
    chown -R appuser:appuser /xdg /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/src /app/src

USER appuser

EXPOSE 8012

CMD ["python", "-m", "password_engine", "api", "--host", "0.0.0.0", "--port", "8012"]
