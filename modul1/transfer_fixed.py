"""Исправление переводов единым порядком захвата блокировок.

В программе нет sleep и timeout. Оба потока всегда берут сначала счёт A,
затем счёт B, поэтому цикл ожидания образоваться не может.
"""

from __future__ import annotations

import threading


accounts = {"A": 1000, "B": 1000}
locks = {"A": threading.Lock(), "B": threading.Lock()}
start_barrier = threading.Barrier(2)


def transfer(src: str, dst: str, amount: int, repetitions: int) -> None:
    start_barrier.wait()
    first, second = sorted((src, dst))
    for _ in range(repetitions):
        with locks[first]:
            with locks[second]:
                if accounts[src] < amount:
                    raise ValueError(f"Недостаточно средств на счёте {src}")
                accounts[src] -= amount
                accounts[dst] += amount


def main() -> None:
    threads = [
        threading.Thread(
            target=transfer,
            args=("A", "B", 10, 100),
            name="кассир-1",
        ),
        threading.Thread(
            target=transfer,
            args=("B", "A", 10, 100),
            name="кассир-2",
        ),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    total = sum(accounts.values())
    print("Исправленный перевод завершён")
    print("Счета:", accounts)
    print("Общая сумма:", total)
    print("Инвариант суммы соблюдён:", total == 2000)
    print("Нарушено условие Коффмана: циклическое ожидание")


if __name__ == "__main__":
    main()
