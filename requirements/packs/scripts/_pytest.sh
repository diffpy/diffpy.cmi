#!/usr/bin/env bash
# Usage:
#   ./_pytest.sh urls.txt
#   ./_pytest.sh https://host/a.tar.gz https://host/b.tgz
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
TMPROOT="$(TMPDIR="$START_DIR" mktemp -d -t .tmp_remote_tests.XXXXXXXX)"
trap 'cd "$START_DIR" 2>/dev/null || true; rm -rf -- "$TMPROOT" || true' EXIT
cd "$TMPROOT"

overall_ec=0
i=0

for url in "${URLS[@]}"; do
  ((++i))
  printf '\n==> [%d] %s\n' "$i" "$url"

  tfile="$(TMPDIR="$TMPROOT" mktemp -t "dl_${i}.XXXXXXXX")"
  tarball="${tfile}.tar.gz"
  curl -L --fail -o "$tarball" "$url"

  pkgdir="$TMPROOT/pkg_${i}"
  mkdir -p "$pkgdir"
  tar -xzf "$tarball" -C "$pkgdir" 2>/dev/null || tar -xf "$tarball" -C "$pkgdir"

  first_entry="$(tar -tzf "$tarball" 2>/dev/null | head -1 || true)"
  if [ -z "$first_entry" ]; then
    first_entry="$(tar -tf "$tarball" 2>/dev/null | head -1 || true)"
  fi

  top="${first_entry%%/*}"
  if [ -n "$top" ] && [ -d "$pkgdir/$top" ]; then
    projroot="$pkgdir/$top"
  else
    projroot="$pkgdir"
  fi

  [ -d "$projroot/src" ] && rm -rf -- "$projroot/src" || true

  if [ -d "$projroot/tests" ]; then
    ( cd "$projroot" && PYTHONPATH="$PWD:tests:${PYTHONPATH:-}" pytest ) || overall_ec=1
  else
    ( cd "$projroot" && PYTHONPATH="$PWD:${PYTHONPATH:-}" pytest ) || overall_ec=1
  fi

  rm -f -- "$tarball" "$tfile" || true
  rm -rf -- "$pkgdir" || true
done

exit "$overall_ec"
