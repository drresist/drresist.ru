#!/bin/sh
set -eu

echo "migrate..."
python manage.py migrate --noinput

echo "import_posts..."
python manage.py import_posts

echo "collectstatic..."
python manage.py collectstatic --noinput

echo "gunicorn on :8000"
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --access-logfile - \
  --error-logfile -
