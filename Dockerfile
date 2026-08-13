# syntax=docker/dockerfile:1

FROM python:3.13-slim AS python-base

ENV VIRTUAL_ENV=/venv \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /app


FROM python-base AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.3 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV \
    UV_LINK_MODE=copy

# Deps only (no dev/test groups); the project itself is not a package.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-default-groups


FROM python-base AS production

ENV ENV=production
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
COPY . /app
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
ENTRYPOINT ["python", "-m", "gymhero.server"]