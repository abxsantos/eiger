#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

# Initializing global variables and functions:
: "${DJANGO_ENV:=development}"

# Fail CI if `DJANGO_ENV` is not set to `development`:
if [ "$DJANGO_ENV" != 'development' ]; then
  echo 'DJANGO_ENV is not set to development. Running tests is not safe.'
  exit 1
fi

mkdir -p reports

cosmic-ray init cosmic-ray.config.ini reports/cosmic-ray-session.sqlite
cosmic-ray --verbosity=INFO baseline cosmic-ray.config.ini
cosmic-ray --verbosity=INFO exec cosmic-ray.config.ini reports/cosmic-ray-session.sqlite
cr-html reports/cosmic-ray-session.sqlite > reports/mutation-report.html
