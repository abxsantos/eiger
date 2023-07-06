#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

source ./scripts/utils.sh

# Initializing global variables and functions:
: "${DJANGO_ENV:=development}"

# Fail CI if `DJANGO_ENV` is not set to `development`:
if [ "$DJANGO_ENV" != 'development' ]; then
  echo 'DJANGO_ENV is not set to development. Running tests is not safe.'
  exit 1
fi

run_ci () {
  echo '[ci started]'
  set -x  # we want to print commands during the CI process.

  # Testing filesystem and permissions:
  touch .perm && rm -f .perm
  touch '/var/www/django/media/.perm' && rm -f '/var/www/django/media/.perm'
  touch '/var/www/django/static/.perm' && rm -f '/var/www/django/static/.perm'

  isort . --check --diff
  blue . --diff
  # Running linting for all python files in the project:
  ruff .
  djlint --check eiger

  # Running type checking, see https://github.com/typeddjango/django-stubs
  # shellcheck disable=SC2046
  mypy manage.py eiger
  mypy tests

  # Running tests:
  pytest --cov=. \
        --cov=tests --cov-branch \
        --cov-report=term-missing:skip-covered \
        --cov-fail-under=95 \
        --junitxml=reports/junit.xml \
        --cov-report=xml:reports/coverage.xml \
        --cov-report=html:reports/html

  # Run checks to be sure we follow all django's best practices:
  python manage.py check --fail-level WARNING

  # Run checks to be sure settings are correct (production flag is required):
  DJANGO_ENV=production python manage.py check --deploy --fail-level WARNING

  # Check that staticfiles app is working fine:
  DJANGO_ENV=production DJANGO_COLLECTSTATIC_DRYRUN=1 \
    python manage.py collectstatic --no-input --dry-run

  # Check that all migrations worked fine:
  python manage.py makemigrations --dry-run --check

  # Check production settings for gunicorn:
  gunicorn --check-config --config python:scripts.gunicorn_config eiger.wsgi

  # Checking if all the dependencies are secure and do not have any
  # known vulnerabilities:
  # TODO: remove once `py` / `pytest` package are updated
  safety check --full-report --ignore=51457

  # Checking `pyproject.toml` file contents:
  poetry check

  # Checking dependencies status:
  pip check

  set +x
  echo '[ci finished]'
}

# Remove any cache before the script:
pyclean

# Run the CI process:
run_ci

# Clean everything up:
trap pyclean EXIT INT TERM
