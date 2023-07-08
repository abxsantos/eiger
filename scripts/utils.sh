#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail


pyclean () {
  # Cleaning cache:
  find . \
    | grep -E '(\.geckodriver.log|\.pytest_cache|\.mypy_cache|\.ruff_cache|__pycache__|\.hypothesis|\.perm|\.cache|\.static|\.py[cod]$)' \
    | xargs rm -rf \
  || true
}
