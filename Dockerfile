# syntax=docker/dockerfile:1.6

FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/root/.local/bin:${PATH}"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# IMPORTANT: venv outside /app so dev bind-mount doesn't hide it
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:${PATH}" \
    PYTHONPATH="/app"

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY . .

# Runtime directories
RUN mkdir -p /app/staticfiles /app/var/celery

# Collect static at build time for prod images (Whitenoise)
ENV DJANGO_SETTINGS_MODULE=config.settings.prod \
    DEBUG="False" \
    SECRET_KEY=build-time-secret \
    ALLOWED_HOSTS=localhost

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
