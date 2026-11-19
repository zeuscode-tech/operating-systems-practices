#!/usr/bin/env python3
"""Трансляция логических адресов через таблицу страниц."""

from pathlib import Path


PAGE_SIZE = 1024
ROOT = Path(__file__).resolve().parent


def load_table(path: Path) -> dict[int, int]:
    table: dict[int, int] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        page, frame = line.split()
        table[int(page)] = int(frame)
    return table


def translate(address: int, table: dict[int, int]) -> str:
    page, offset = divmod(address, PAGE_SIZE)
    if page not in table:
        return (
            f"{address}: стр. {page}, смещ. {offset} "
            "→ страница отсутствует"
        )
    frame = table[page]
    physical = frame * PAGE_SIZE + offset
    return (
        f"{address}: стр. {page}, смещ. {offset} "
        f"→ кадр {frame} → физический адрес {physical}"
    )


def main() -> None:
    table = load_table(ROOT / "pagetable.txt")
    addresses = [
        int(line)
        for line in (ROOT / "refs.txt").read_text().splitlines()
        if line.strip()
    ]
    for address in addresses:
        print(translate(address, table))


if __name__ == "__main__":
    main()
