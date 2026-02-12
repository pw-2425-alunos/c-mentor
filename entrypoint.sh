#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
gunicorn projeto.wsgi:application \
    --bind 0.0.0.0:3000 \
    --workers 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - &

# Espera que o Gunicorn suba
sleep 10

# Mantém container vivo
wait
