#!/bin/sh
# Runs the five exact verification scripts for the hazard-mixture note.
# Usage: PYTHON=/path/to/python ./run_all.sh   (needs sympy >= 1.12)
set -e
PY="${PYTHON:-python3}"
cd "$(dirname "$0")"
status=0
for s in verify_core.py verify_general_mechanism.py verify_strict_variant.py verify_two_crossings.py verify_reversed_hazard.py; do
  echo "== $s =="
  if "$PY" "$s"; then echo "== $s: OK =="; else echo "== $s: FAILED =="; status=1; fi
done
exit $status
