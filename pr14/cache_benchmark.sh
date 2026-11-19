#!/usr/bin/env bash
set -euo pipefail

WORK=$(mktemp -d "${TMPDIR:-/tmp}/pr14-cache.XXXXXX")
trap 'rm -rf "$WORK"' EXIT
FILE="$WORK/data.bin"
dd if=/dev/zero of="$FILE" bs=1M count=64 status=none

if test "${1:-}" = "--drop-caches"; then
    test "$(uname -s)" = Linux || { echo 'Сброс кэша поддержан только в Linux' >&2; exit 1; }
    test "$(id -u)" -eq 0 || { echo 'Для --drop-caches нужен root' >&2; exit 1; }
    sync
    echo 3 > /proc/sys/vm/drop_caches
fi

echo 'Первое чтение:'
time dd if="$FILE" of=/dev/null bs=1M status=none
echo 'Повторное чтение (page cache):'
time dd if="$FILE" of=/dev/null bs=1M status=none
