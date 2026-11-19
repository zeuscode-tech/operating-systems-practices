#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
python3 disk.py | tee disk_output.txt
python3 starvation.py | tee starvation_output.txt

grep -Eq '^FCFS +640 ' disk_output.txt
grep -Eq '^SSTF +236 ' disk_output.txt
grep -Eq '^SCAN +331 ' disk_output.txt
grep -Eq '^C-SCAN +382 ' disk_output.txt
grep -Eq '^LOOK +299 ' disk_output.txt
grep -Eq '^C-LOOK +322 ' disk_output.txt
echo 'ПР-13: контрольные значения совпали'
