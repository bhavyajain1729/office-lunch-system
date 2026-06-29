#!/bin/sh

set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating admin user (if needed)..."
if [ ! -z "$ADMIN_EMAIL" ] && [ ! -z "$ADMIN_PASSWORD" ]; then
    python manage.py promote_admin \
        --email "$ADMIN_EMAIL" \
        --create \
        --password "$ADMIN_PASSWORD" \
        --full-name "Office Lunch Admin" || true
fi

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3