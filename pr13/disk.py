#!/usr/bin/env python3
"""Симулятор FCFS, SSTF, SCAN, C-SCAN, LOOK и C-LOOK."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CYLINDERS = 200
HEAD = 53
REQUESTS = [98, 183, 37, 122, 14, 124, 65, 67]


def distance(head: int, order: list[int]) -> int:
    total = 0
    current = head
    for cylinder in order:
        total += abs(current - cylinder)
        current = cylinder
    return total


def fcfs(requests: list[int], head: int) -> list[int]:
    return requests.copy()


def sstf(requests: list[int], head: int) -> list[int]:
    pending = requests.copy()
    order: list[int] = []
    current = head
    while pending:
        chosen = min(pending, key=lambda value: (abs(value - current), value))
        order.append(chosen)
        pending.remove(chosen)
        current = chosen
    return order


def scan(requests: list[int], head: int, limit: int = CYLINDERS) -> list[int]:
    up = sorted(value for value in requests if value >= head)
    down = sorted((value for value in requests if value < head), reverse=True)
    endpoint = [limit - 1] if down and (not up or up[-1] != limit - 1) else []
    return up + endpoint + down


def cscan(requests: list[int], head: int, limit: int = CYLINDERS) -> list[int]:
    up = sorted(value for value in requests if value >= head)
    down = sorted(value for value in requests if value < head)
    if not down:
        return up
    tail = [] if up and up[-1] == limit - 1 else [limit - 1]
    start = [] if down and down[0] == 0 else [0]
    return up + tail + start + down


def look(requests: list[int], head: int) -> list[int]:
    return sorted(value for value in requests if value >= head) + sorted(
        (value for value in requests if value < head), reverse=True
    )


def clook(requests: list[int], head: int) -> list[int]:
    return sorted(value for value in requests if value >= head) + sorted(
        value for value in requests if value < head
    )


ALGORITHMS = {
    "FCFS": fcfs,
    "SSTF": sstf,
    "SCAN": scan,
    "C-SCAN": cscan,
    "LOOK": look,
    "C-LOOK": clook,
}


def evaluate(requests: list[int], head: int) -> list[tuple[str, list[int], int]]:
    return [
        (name, algorithm(requests, head), distance(head, algorithm(requests, head)))
        for name, algorithm in ALGORITHMS.items()
    ]


def main() -> None:
    print(f"Цилиндры: 0..{CYLINDERS - 1}")
    print(f"Начальная позиция: {HEAD}")
    print("Очередь:", REQUESTS)
    print("\nалгоритм  перемещение  порядок обслуживания")
    rows = evaluate(REQUESTS, HEAD)
    for name, order, total in rows:
        print(f"{name:<9} {total:>11}  {' -> '.join(map(str, order))}")

    with (ROOT / "disk_results.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["algorithm", "movement", "order"])
        for name, order, total in rows:
            writer.writerow([name, total, " ".join(map(str, order))])


if __name__ == "__main__":
    main()
