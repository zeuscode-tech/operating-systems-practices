#!/usr/bin/env python3
"""Проверка структуры итоговой сдачи без изменения системы."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = {
    1: "pr01", 2: "pr02", 3: "pr03", 4: "pr04",
    5: "pr05", 6: "pr06", 7: "pr07", 8: "pr08",
    9: "practice - 9", 10: "pr10", 11: "practice - 11",
    12: "pr12", 13: "pr13", 14: "pr14", 15: "pr15", 16: "pr16",
}
EVIDENCE = {
    9: ["compare.py", "allocator-c/my_alloc.c"],
    10: ["translate.py", "tlb_sim.py", "tlb_results.csv"],
    11: ["replace.py", "faults.c", "faults_vs_frames.png"],
    12: ["dedup.py", "fs_model.py", "memfs.py"],
    13: ["disk.py", "starvation.py"],
    14: ["io_benchmark.c", "fifo_wait.py", "direct_io.c"],
    15: ["app.py", "Dockerfile", "compose.yaml"],
    16: ["DEFENSE_CHECKLIST.md", "RK2_PREP.md"],
}


def main() -> None:
    missing: list[str] = []
    for number, directory_name in DIRECTORIES.items():
        directory = ROOT / directory_name
        if not directory.is_dir():
            missing.append(directory_name)
            continue
        if not (directory / "README.md").is_file():
            missing.append(f"{directory_name}/README.md")
        for relative in EVIDENCE.get(number, []):
            if not (directory / relative).is_file():
                missing.append(f"{directory_name}/{relative}")

    if missing:
        print("Не хватает файлов:")
        for path in missing:
            print(" -", path)
        raise SystemExit(1)
    print("ПР-1…ПР-16: структура и ключевые доказательства на месте")


if __name__ == "__main__":
    main()
