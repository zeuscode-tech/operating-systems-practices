#!/usr/bin/env bash
set -euo pipefail

command -v docker >/dev/null || { echo 'Нужен Docker' >&2; exit 1; }
echo '=== PID внутри отдельного namespace ==='
docker run --rm alpine sh -c 'echo "PID контейнера: $$"; ps'
echo
echo '=== Тот же образ с PID namespace хоста ==='
docker run --rm --pid=host alpine sh -c 'ps | head'
echo 'Контейнер обычно видит собственное дерево процессов; --pid=host снимает эту изоляцию.'
