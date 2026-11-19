#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
python3 -m unittest -v test_app.py 2>&1 | tee test_output.txt
grep -q 'Ran 3 tests' test_output.txt
grep -q '^FROM python:' Dockerfile
grep -q '^USER app' Dockerfile
echo 'ПР-15: переносимые проверки пройдены'
