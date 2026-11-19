#!/usr/bin/env bash
set -euo pipefail

if test "${1:-}" != "--run"; then
    echo "Скрипт создаёт и монтирует временный ext4-образ. Запуск: sudo $0 --run" >&2
    exit 2
fi
test "$(uname -s)" = Linux || { echo 'Нужен Linux' >&2; exit 1; }
test "$(id -u)" -eq 0 || { echo 'Нужен root' >&2; exit 1; }

ROOT=$(mktemp -d /tmp/pr12-ext4.XXXXXX)
IMAGE="$ROOT/fs.img"
MOUNT="$ROOT/mnt"
mkdir "$MOUNT"

cleanup() {
    mountpoint -q "$MOUNT" && umount "$MOUNT" || true
    rm -rf "$ROOT"
}
trap cleanup EXIT

dd if=/dev/zero of="$IMAGE" bs=1M count=64 status=none
mkfs.ext4 -q -N 1024 "$IMAGE"
mount -o loop "$IMAGE" "$MOUNT"
echo 'До создания файлов:'
df -h "$MOUNT"
df -i "$MOUNT"

for index in $(seq 1 1100); do
    touch "$MOUNT/file-$index" 2>/dev/null || break
done

echo 'После создания файлов:'
df -h "$MOUNT"
df -i "$MOUNT"
