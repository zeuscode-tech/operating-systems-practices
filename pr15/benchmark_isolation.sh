#!/usr/bin/env bash
set -euo pipefail

command -v docker >/dev/null || { echo 'Нужен Docker' >&2; exit 1; }
echo 'Пять запусков короткого процесса в контейнере:'
for run in 1 2 3 4 5; do
    TIMEFORMAT="запуск $run: %3R с"
    time docker run --rm alpine true
done
echo 'Контейнер использует ядро хоста, поэтому обычно стартует быстрее полноценной VM.'
