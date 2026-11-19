#!/usr/bin/env python3
"""Наглядный пример голодания дальнего запроса в SSTF."""

from __future__ import annotations

from disk import clook, distance, sstf


def main() -> None:
    head = 50
    far = 190
    near_stream = [51, 49, 52, 48, 53, 47, 54, 46, 55, 45, 56, 44]
    requests = [far, *near_stream]
    sstf_order = sstf(requests, head)
    clook_order = clook(requests, head)

    print("Запрос 190 пришёл первым, затем постоянно поступают близкие запросы.")
    print("SSTF:", " -> ".join(map(str, sstf_order)))
    print("C-LOOK:", " -> ".join(map(str, clook_order)))
    print(f"Позиция дальнего запроса в SSTF: {sstf_order.index(far) + 1} из {len(requests)}")
    print(f"Перемещение SSTF: {distance(head, sstf_order)}")
    print(f"Перемещение C-LOOK: {distance(head, clook_order)}")
    print("Вывод: SSTF минимизирует ближайший шаг, но может долго откладывать дальние запросы.")


if __name__ == "__main__":
    main()
