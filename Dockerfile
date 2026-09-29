FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY manage.py .
COPY config/ config/
COPY blog/ blog/
COPY posts/ posts/
COPY static/ static/
COPY scripts/entrypoint.sh scripts/entrypoint.sh

RUN chmod +x scripts/entrypoint.sh \
    && useradd --create-home --uid 10001 app \
    && mkdir -p staticfiles media \
    && chown -R app:app /app

USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

ENTRYPOINT ["scripts/entrypoint.sh"]
