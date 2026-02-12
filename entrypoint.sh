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

# Espera que Gunicorn esteja pronto na porta 3000
echo "Waiting for Gunicorn to be ready..."
while ! nc -z localhost 3000; do   
  sleep 1
done

echo "Gunicorn is up!"

# Mantém o container vivo
wait
