#!/bin/sh
# Run database migrations then start the API server.
# Set SKIP_MIGRATIONS=true to skip migrations (e.g. when running the image
# in isolation for smoke tests without a live database).
set -e

if [ "${SKIP_MIGRATIONS:-false}" != "true" ]; then
    alembic upgrade head
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
