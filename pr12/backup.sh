#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Использование: $0 backup SOURCE BACKUP_DIR | restore BACKUP_DIR TARGET" >&2
    exit 2
}

test "$#" -eq 3 || usage
MODE=$1
SOURCE=$2
TARGET=$3
LOG="${TARGET%/}.log"

copy_tree() {
    local from=$1
    local to=$2
    mkdir -p "$to"
    if command -v rsync >/dev/null 2>&1; then
        # --checksum замечает изменение содержимого даже при одинаковых размере
        # и временной метке (частый случай в быстрых автоматических тестах).
        rsync -a --checksum --delete --itemize-changes "$from/" "$to/"
    else
        cp -a "$from/." "$to/"
    fi
}

case "$MODE" in
    backup)
        test -d "$SOURCE" || { echo "Нет исходного каталога: $SOURCE" >&2; exit 1; }
        mkdir -p "$TARGET"
        {
            echo "$(date -u +%FT%TZ) backup $SOURCE -> $TARGET"
            copy_tree "$SOURCE" "$TARGET"
        } | tee -a "$LOG"
        ;;
    restore)
        test -d "$SOURCE" || { echo "Нет резервной копии: $SOURCE" >&2; exit 1; }
        mkdir -p "$TARGET"
        {
            echo "$(date -u +%FT%TZ) restore $SOURCE -> $TARGET"
            copy_tree "$SOURCE" "$TARGET"
        } | tee -a "$LOG"
        ;;
    *) usage ;;
esac
