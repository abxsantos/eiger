#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

# We are using `gunicorn` for production, see:
# http://docs.gunicorn.org/en/stable/configure.html


# Run python specific scripts:
# Running migrations in startup script might not be the best option, see:
# docs/pages/template/production-checklist.rst
echo "Migrating..."
python manage.py migrate --noinput
echo "Migrated successfully."
echo "Collecting static..."
python manage.py collectstatic --noinput --clear
echo "Collected static successfully."

# Start gunicorn:
# Docs: http://docs.gunicorn.org/en/stable/settings.html
# Make sure it is in sync with `django/ci.sh` check:
gunicorn \
  --config python:scripts.gunicorn_config \
  eiger.wsgi
