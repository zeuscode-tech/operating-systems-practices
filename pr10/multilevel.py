#!/usr/bin/env python3
"""Упрощённая двухуровневая таблица страниц."""

PAGE_SIZE = 1024
L2_ENTRIES = 4
FLAT_TABLE = {0: 5, 1: 2, 2: 7, 3: 0}


def build_two_level(table: dict[int, int]) -> dict[int, dict[int, int]]:
    result: dict[int, dict[int, int]] = {}
    for page, frame in table.items():
        first, second = divmod(page, L2_ENTRIES)
        result.setdefault(first, {})[second] = frame
    return result


def translate(address: int, table: dict[int, dict[int, int]]) -> str:
    page, offset = divmod(address, PAGE_SIZE)
    first, second = divmod(page, L2_ENTRIES)
    if first not in table or second not in table[first]:
        return f"{address}: страница {page} отсутствует"
    frame = table[first][second]
    physical = frame * PAGE_SIZE + offset
    return (
        f"{address}: L1={first}, L2={second}, кадр={frame}, "
        f"физический={physical}"
    )


def main() -> None:
    table = build_two_level(FLAT_TABLE)
    print("Двухуровневая таблица:", table)
    for address in (1200, 3100, 5000):
        print(translate(address, table))
    print("Без TLB: 2 обращения к таблицам + 1 к данным = 3 обращения.")


if __name__ == "__main__":
    main()
