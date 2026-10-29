#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$project_dir"
mkdir -p outputs
export PYTHONPYCACHEPREFIX="$project_dir/.pycache"

python3 -m py_compile \
  transfer_deadlock.py transfer_fixed.py banker.py wait_graph.py \
  tracked_lock.py transfer_tracked.py philosophers.py test_project.py

python3 -m unittest -v test_project.py 2>&1 | tee outputs/tests.txt

python3 transfer_fixed.py | tee outputs/transfer_fixed.txt
python3 banker.py data/bank_state.txt data/bank_state2.txt \
  --requests data/requests.txt | tee outputs/banker.txt
python3 wait_graph.py data/waitlog.txt | tee outputs/wait_graph.txt
python3 transfer_tracked.py | tee outputs/tracked_lock.txt
python3 philosophers.py --duration 10 | tee outputs/philosophers.txt

echo "Все безопасно завершающиеся проверки выполнены."
echo "Исходный deadlock запускайте отдельно: python3 transfer_deadlock.py"
