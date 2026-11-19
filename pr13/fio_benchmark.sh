#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
command -v fio >/dev/null || { echo 'Установите fio: sudo apt install fio' >&2; exit 1; }
truncate -s 64M fio-test.bin
trap 'rm -f fio-test.bin' EXIT
fio fio/read-only.fio | tee fio_output.txt
