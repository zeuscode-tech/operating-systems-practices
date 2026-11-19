#!/usr/bin/env python3
"""Модель LRU-TLB и график зависимости hit ratio от размера."""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
import csv
import random

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from translate import PAGE_SIZE, load_table


ROOT = Path(__file__).resolve().parent
TLB_NS = 10
MEMORY_NS = 100


class LRUTLB:
    def __init__(self, capacity: int):
        if capacity < 1:
            raise ValueError("capacity должна быть положительной")
        self.capacity = capacity
        self.entries: OrderedDict[int, int] = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.page_faults = 0

    def access(self, address: int, table: dict[int, int]) -> int | None:
        page, offset = divmod(address, PAGE_SIZE)
        if page in self.entries:
            self.hits += 1
            frame = self.entries.pop(page)
            self.entries[page] = frame
        else:
            self.misses += 1
            if page not in table:
                self.page_faults += 1
                return None
            frame = table[page]
            if len(self.entries) == self.capacity:
                self.entries.popitem(last=False)
            self.entries[page] = frame
        return frame * PAGE_SIZE + offset

    @property
    def hit_ratio(self) -> float:
        translations = self.hits + self.misses
        return self.hits / translations if translations else 0.0


def effective_access_time(hit_ratio: float) -> float:
    hit = TLB_NS + MEMORY_NS
    miss = TLB_NS + 2 * MEMORY_NS
    return hit_ratio * hit + (1 - hit_ratio) * miss


def local_refs(count: int = 2000, seed: int = 42) -> list[int]:
    rng = random.Random(seed)
    refs: list[int] = []
    current = 0
    for _ in range(count):
        if rng.random() < 0.86:
            page = current
        else:
            page = rng.randrange(4)
            current = page
        refs.append(page * PAGE_SIZE + rng.randrange(PAGE_SIZE))
    return refs


def simulate(capacity: int, refs: list[int], table: dict[int, int]) -> LRUTLB:
    tlb = LRUTLB(capacity)
    for address in refs:
        tlb.access(address, table)
    return tlb


def main() -> None:
    table = load_table(ROOT / "pagetable.txt")
    refs = local_refs()
    rows: list[tuple[int, float, float, int]] = []

    print("размер | hits | misses | hit ratio | EAT, нс")
    for size in range(1, 9):
        tlb = simulate(size, refs, table)
        eat = effective_access_time(tlb.hit_ratio)
        rows.append((size, tlb.hit_ratio, eat, tlb.page_faults))
        print(
            f"{size:>6} | {tlb.hits:>4} | {tlb.misses:>6} | "
            f"{tlb.hit_ratio:>9.3f} | {eat:>7.1f}"
        )

    with (ROOT / "tlb_results.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["tlb_size", "hit_ratio", "eat_ns", "page_faults"])
        writer.writerows(rows)

    plt.figure(figsize=(7, 4))
    plt.plot([row[0] for row in rows], [row[1] for row in rows], marker="o")
    plt.ylim(0, 1.02)
    plt.xlabel("Размер TLB, записей")
    plt.ylabel("Доля попаданий")
    plt.title("Локальность обращений и эффективность TLB")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(ROOT / "tlb_hit_ratio.png", dpi=160)
    plt.close()

    print("\nТеоретический EAT:")
    for ratio in (0.80, 0.90, 0.98):
        print(f"hit={ratio:.0%}: {effective_access_time(ratio):.1f} нс")
    print(f"Без TLB: {2 * MEMORY_NS} нс")


if __name__ == "__main__":
    main()
