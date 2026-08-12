# ============================================================
# FMG — multi-stage Dockerfile
#
# Targets:
#   dev      -> used by fmg_dev / fmg_test compose (bind-mounted
#               code, dev+test extras installed: pytest/ruff/mypy)
#   runtime  -> used by prod compose (immutable, no dev deps,
#               non-root user)
#
# ============================================================

# ---- base: shared runtime OS packages only ----
FROM python:3.11.9-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /code
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# ---- builder: adds compilers, installs dev+test deps ----
FROM base AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml /code/
RUN pip install --no-cache-dir --user -e ".[dev]"
ENV PATH=/root/.local/bin:$PATH

# ---- dev: what fmg_dev / fmg_test actually run ----
FROM builder AS dev
COPY . /code/
# code gets overlaid by the bind mount (.:/code) in fmg_dev/fmg_test —
# this COPY just keeps the image runnable standalone too (e.g. in CI)

# ---- runtime: slim, no dev deps, non-root — what prod runs ----
FROM base AS runtime
RUN useradd --create-home --shell /bin/bash appuser
COPY pyproject.toml /code/
RUN pip install --no-cache-dir .
COPY --chown=appuser:appuser . /code/
USER appuser
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
