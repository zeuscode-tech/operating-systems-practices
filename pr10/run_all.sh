#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

python3 translate.py | tee translate_output.txt
python3 tlb_sim.py | tee tlb_output.txt
python3 multilevel.py | tee multilevel_output.txt
python3 memtour.py | tee memtour_output.txt

cc -std=c11 -O2 -Wall -Wextra -Werror tlb_stride.c -o tlb_stride
./tlb_stride | tee tlb_stride_output.txt
