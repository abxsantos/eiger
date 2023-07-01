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

# Remove any cache before the script:
pyclean

pytest tests/test_eiger

# Clean everything up:
trap pyclean EXIT INT TERM