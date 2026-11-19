#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
WORK=$(mktemp -d "${TMPDIR:-/tmp}/pr12.XXXXXX")
trap 'rm -rf "$WORK"' EXIT
./setup_demo.sh "$WORK/demo-work"

mkdir -p "$WORK/demo-work/backup-source"
printf 'версия 1\n' > "$WORK/demo-work/backup-source/a.txt"
./backup.sh backup "$WORK/demo-work/backup-source" "$WORK/demo-work/backup"
printf 'версия 2\n' > "$WORK/demo-work/backup-source/a.txt"
printf 'новый файл\n' > "$WORK/demo-work/backup-source/b.txt"
./backup.sh backup "$WORK/demo-work/backup-source" "$WORK/demo-work/backup"
./backup.sh restore "$WORK/demo-work/backup" "$WORK/demo-work/restored"
cmp "$WORK/demo-work/backup-source/a.txt" "$WORK/demo-work/restored/a.txt"
cmp "$WORK/demo-work/backup-source/b.txt" "$WORK/demo-work/restored/b.txt"

mkdir -p "$WORK/demo-work/duplicates"
printf 'одинаковое содержимое\n' > "$WORK/demo-work/duplicates/one.txt"
cp "$WORK/demo-work/duplicates/one.txt" "$WORK/demo-work/duplicates/two.txt"
python3 dedup.py "$WORK/demo-work/duplicates" --apply | tee dedup_output.txt
test "$(stat -f %i "$WORK/demo-work/duplicates/one.txt" 2>/dev/null || stat -c %i "$WORK/demo-work/duplicates/one.txt")" = "$(stat -f %i "$WORK/demo-work/duplicates/two.txt" 2>/dev/null || stat -c %i "$WORK/demo-work/duplicates/two.txt")"

python3 fs_model.py | tee allocation_output.txt
echo 'ПР-12: переносимые проверки пройдены'
