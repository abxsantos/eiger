#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

source ./scripts/utils.sh

pyclean

isort .
blue .
ruff --fix .
djlint --lint --reformat eiger
mypy manage.py eiger
mypy tests

# Clean everything up:
trap pyclean EXIT INT TERM
