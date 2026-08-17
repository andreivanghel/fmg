# ============================================================
# FMG — multi-stage Dockerfile (uv-managed dependencies)
#
# Targets:
#   dev      -> fmg_dev / fmg_test compose (bind-mounted code,
#               "dev" extra installed: pytest/ruff/mypy)
#   runtime  -> prod compose (immutable, no dev deps, non-root)
#
# ATTENZIONE al bind mount: uv per default mette il venv dentro
# /code/.venv. Ma fmg_dev/fmg_test montano `.:/code` — quindi il
# venv costruito nell'immagine verrebbe NASCOSTO dal mount al
# primo avvio (il tuo host non ha quel .venv, quindi Docker
# monta una cartella "vuota" sopra). Per questo UV_PROJECT_ENVIRONMENT
# punta a /opt/venv, FUORI da /code — così il mount non lo tocca.
# ============================================================

FROM python:3.11.9-slim AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"
WORKDIR /code
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# ---- dev: compilers + extra "dev" completo — usato da fmg_dev/fmg_test ----
FROM base AS dev
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml uv.lock /code/
RUN uv sync --frozen --no-install-project
COPY . /code/
RUN uv sync --frozen
# la COPY sopra viene comunque sovrascritta dal bind mount .:/code in
# fmg_dev/fmg_test — serve solo a rendere l'immagine eseguibile da sola

# ---- runtime: slim, no dev deps, non-root — usato da prod ----
FROM base AS runtime
RUN useradd --create-home --shell /bin/bash appuser
COPY pyproject.toml uv.lock /code/
RUN uv sync --frozen --no-install-project --no-dev
COPY --chown=appuser:appuser . /code/
RUN uv sync --frozen --no-dev
USER appuser
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
