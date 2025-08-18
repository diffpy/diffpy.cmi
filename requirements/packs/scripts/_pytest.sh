#!/usr/bin/env bash
# Usage:
#   ./run-remote-tests.sh urls.txt
#   ./run-remote-tests.sh https://host/a.tar.gz https://host/b.tgz
# From ChatGPT

set -euo pipefail

URLS=()
if (($# == 1)) && [ -f "$1" ]; then
  URLS_FILE="$1"
  case "$URLS_FILE" in /*) ;; *) URLS_FILE="$PWD/$URLS_FILE" ;; esac
  while IFS= read -r line; do
    [[ -z "${line// }" || "$line" =~ ^[[:space:]]*# ]] && continue
    URLS+=("$line")
  done < "$URLS_FILE"
else
  URLS=("$@")
fi

START_DIR="$PWD"
TMPROOT="$(mktemp -d -p "$START_DIR" ".tmp_remote_tests.XXXXXX")"
trap 'cd "$START_DIR" 2>/dev/null || true; rm -rf -- "$TMPROOT"' EXIT
cd "$TMPROOT"

overall_ec=0
i=0
for url in "${URLS[@]}"; do
  ((i++))
  echo -e "\n==> [$i] $url"

  tarball="$(mktemp -p "$TMPROOT" "dl_${i}.XXXXXX.tar.gz")"
  curl -L --fail -o "$tarball" "$url"

  pkgdir="$TMPROOT/pkg_${i}"
  mkdir -p "$pkgdir"
  tar -xzf "$tarball" -C "$pkgdir"

  first_entry="$(tar -tzf "$tarball" | head -1 || true)"
  top="${first_entry%%/*}"
  if [ -n "$top" ] && [ -d "$pkgdir/$top" ]; then
    projroot="$pkgdir/$top"
  else
    projroot="$pkgdir"
  fi

  if [ -d "$projroot/src" ]; then
    rm -rf -- "$projroot/src"
  fi

  if [ -d "$projroot/tests" ]; then
    ( cd "$projroot" && PYTHONPATH="$PWD:tests:${PYTHONPATH:-}" pytest ) || overall_ec=1
  else
    ( cd "$projroot" && PYTHONPATH="$PWD:${PYTHONPATH:-}" pytest ) || overall_ec=1
  fi

  rm -f -- "$tarball"
  rm -rf -- "$pkgdir"
done

exit "$overall_ec"
