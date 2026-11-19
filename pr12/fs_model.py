#!/usr/bin/env python3
"""Сравнение непрерывного, связанного и индексного размещения."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DISK_SIZE = 128


@dataclass
class Result:
    method: str
    allocated: int
    failed: int
    random_access_steps: float
    largest_free_run: int


def largest_run(disk: list[str | None]) -> int:
    best = current = 0
    for block in disk:
        current = current + 1 if block is None else 0
        best = max(best, current)
    return best


def free_blocks(disk: list[str | None], name: str) -> None:
    for index, owner in enumerate(disk):
        if owner == name or owner == f"{name}:index":
            disk[index] = None


def allocate_contiguous(disk: list[str | None], name: str, size: int) -> list[int]:
    for start in range(len(disk) - size + 1):
        if all(block is None for block in disk[start : start + size]):
            for index in range(start, start + size):
                disk[index] = name
            return list(range(start, start + size))
    return []


def allocate_linked(disk: list[str | None], name: str, size: int) -> list[int]:
    free = [index for index, block in enumerate(disk) if block is None]
    if len(free) < size:
        return []
    chosen = free[::2] + free[1::2]
    chosen = chosen[:size]
    for index in chosen:
        disk[index] = name
    return chosen


def allocate_indexed(disk: list[str | None], name: str, size: int) -> list[int]:
    free = [index for index, block in enumerate(disk) if block is None]
    if len(free) < size + 1:
        return []
    disk[free[0]] = f"{name}:index"
    for index in free[1 : size + 1]:
        disk[index] = name
    return free[: size + 1]


def simulate(method: str) -> Result:
    disk: list[str | None] = [None] * DISK_SIZE
    allocator = {
        "contiguous": allocate_contiguous,
        "linked": allocate_linked,
        "indexed": allocate_indexed,
    }[method]
    operations = [
        ("alloc", "A", 24),
        ("alloc", "B", 18),
        ("alloc", "C", 22),
        ("free", "B", 0),
        ("alloc", "D", 30),
        ("free", "A", 0),
        ("alloc", "E", 28),
    ]
    files: dict[str, list[int]] = {}
    failures = 0
    for command, name, size in operations:
        if command == "free":
            free_blocks(disk, name)
            files.pop(name, None)
            continue
        blocks = allocator(disk, name, size)
        if blocks:
            files[name] = blocks
        else:
            failures += 1

    if method == "contiguous":
        access = 1.0
    elif method == "linked":
        access = sum(max(1, len(blocks) / 2) for blocks in files.values()) / len(files)
    else:
        access = 2.0
    return Result(method, len(files), failures, access, largest_run(disk))


def main() -> None:
    results = [simulate(name) for name in ("contiguous", "linked", "indexed")]
    print("method      files failures random_access_steps largest_free_run")
    for result in results:
        print(
            f"{result.method:<11} {result.allocated:>5} {result.failed:>8} "
            f"{result.random_access_steps:>19.1f} {result.largest_free_run:>16}"
        )
    with (ROOT / "allocation_results.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(Result.__annotations__)
        for result in results:
            writer.writerow(result.__dict__.values())


if __name__ == "__main__":
    main()
