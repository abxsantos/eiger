pyclean () {
  # Cleaning cache:
  find . \
    | grep -E '(__pycache__|\.hypothesis|\.perm|\.cache|\.static|\.py[cod]$)' \
    | xargs rm -rf \
  || true
}
