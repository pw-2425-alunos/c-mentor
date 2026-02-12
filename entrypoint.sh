#!/bin/sh
set -e

echo "Migrating database..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Starting Gunicorn..."
exec gunicorn projeto.wsgi:application \
    --bind 0.0.0.0:3000 \
    --workers 3 \
    --threads 2 \
    --access-logfile - \
    --error-logfile -
