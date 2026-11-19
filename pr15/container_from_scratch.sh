#!/usr/bin/env bash
set -euo pipefail

if test "${1:-}" != "--run"; then
    echo "Демонстрация namespaces/chroot. Запуск в учебной Ubuntu: sudo $0 --run" >&2
    exit 2
fi
test "$(uname -s)" = Linux || { echo 'Нужен Linux' >&2; exit 1; }
test "$(id -u)" -eq 0 || { echo 'Нужен root' >&2; exit 1; }
command -v busybox >/dev/null || { echo 'Установите busybox-static' >&2; exit 1; }

ROOT=$(mktemp -d /tmp/pr15-rootfs.XXXXXX)
cleanup() { rm -rf "$ROOT"; }
trap cleanup EXIT
mkdir -p "$ROOT/bin" "$ROOT/proc" "$ROOT/tmp"
cp "$(command -v busybox)" "$ROOT/bin/busybox"
for command in sh ps mount hostname; do ln -s busybox "$ROOT/bin/$command"; done

unshare --fork --pid --mount --uts --mount-proc="$ROOT/proc" \
    chroot "$ROOT" /bin/sh -c 'hostname pr15-container; echo "PID=$$ hostname=$(hostname)"; ps'
