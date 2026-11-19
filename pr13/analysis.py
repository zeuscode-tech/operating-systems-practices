#!/usr/bin/env python3
"""Сравнение алгоритмов на случайных очередях и построение графика."""

from __future__ import annotations

import csv
import random
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from disk import ALGORITHMS, CYLINDERS, distance


ROOT = Path(__file__).resolve().parent


def main() -> None:
    totals: dict[str, list[int]] = defaultdict(list)
    for seed in range(20):
        randomizer = random.Random(seed)
        requests = [randomizer.randrange(CYLINDERS) for _ in range(50)]
        head = randomizer.randrange(CYLINDERS)
        for name, algorithm in ALGORITHMS.items():
            totals[name].append(distance(head, algorithm(requests, head)))

    averages = {name: sum(values) / len(values) for name, values in totals.items()}
    print("Среднее перемещение по 20 очередям из 50 запросов")
    for name, value in averages.items():
        print(f"{name:<9} {value:8.1f}")

    with (ROOT / "random_results.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["algorithm", "average_movement"])
        writer.writerows(averages.items())

    names = list(averages)
    values = [averages[name] for name in names]
    figure, axis = plt.subplots(figsize=(8, 4.5))
    bars = axis.bar(names, values, color="#3b82f6")
    axis.bar_label(bars, fmt="%.0f", padding=3)
    axis.set_ylabel("Среднее перемещение головки")
    axis.set_title("Сравнение алгоритмов планирования диска")
    axis.grid(axis="y", alpha=0.25)
    figure.tight_layout()
    figure.savefig(ROOT / "disk_comparison.png", dpi=160)


if __name__ == "__main__":
    main()
