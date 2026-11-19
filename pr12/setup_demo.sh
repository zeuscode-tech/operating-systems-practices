#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-demo-work}"
if test -e "$ROOT"; then
    echo "Каталог уже существует: $ROOT" >&2
    exit 1
fi
mkdir -p "$ROOT/source" "$ROOT/links" "$ROOT/find"

printf 'важные данные\n' > "$ROOT/source/original.txt"
ln "$ROOT/source/original.txt" "$ROOT/links/hard.txt"
ln -s ../source/original.txt "$ROOT/links/symbolic.txt"
chmod 640 "$ROOT/source/original.txt"

dd if=/dev/zero of="$ROOT/find/large.bin" bs=1048576 count=2 status=none
printf 'маленький файл\n' > "$ROOT/find/small.txt"

{
    echo '=== До удаления исходного имени ==='
    ls -li "$ROOT/source/original.txt" "$ROOT/links/hard.txt" "$ROOT/links/symbolic.txt"
    echo
    echo '=== Файлы больше 1 МиБ ==='
    find "$ROOT" -type f -size +1M -print
    echo
    echo '=== Файлы, изменённые за последние сутки ==='
    find "$ROOT" -type f -mtime -1 -print
} | tee "$ROOT/evidence.txt"

rm "$ROOT/source/original.txt"
{
    echo
    echo '=== После удаления исходного имени ==='
    ls -li "$ROOT/links/hard.txt"
    if test -e "$ROOT/links/symbolic.txt"; then
        echo 'Символическая ссылка работает'
    else
        echo 'Символическая ссылка сломана: её путь больше не существует'
    fi
    echo "Жёсткая ссылка хранит данные: $(cat "$ROOT/links/hard.txt")"
} | tee -a "$ROOT/evidence.txt"
