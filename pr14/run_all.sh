#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
python3 fifo_wait.py | tee fifo_output.txt
grep -q 'blocking' fifo_output.txt

if test "${SKIP_C:-0}" != 1 && command -v cc >/dev/null 2>&1; then
    cc -std=c11 -Wall -Wextra -Werror -pedantic io_benchmark.c -o io_benchmark
    ./io_benchmark 4 | tee io_output.txt
    cc -std=c11 -Wall -Wextra -Werror direct_io.c -o direct_io
    ./direct_io | tee direct_io_output.txt
fi
echo 'ПР-14: переносимые проверки пройдены'
