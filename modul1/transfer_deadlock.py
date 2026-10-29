"""Исходная программа варианта 2: намеренная взаимоблокировка.

Запуск: python3 transfer_deadlock.py
Через 5 секунд faulthandler печатает стеки потоков и завершает процесс.
"""

import faulthandler
import threading
import time


faulthandler.dump_traceback_later(5, exit=True)

accounts = {"A": 1000, "B": 1000}
locks = {"A": threading.Lock(), "B": threading.Lock()}


def transfer(src: str, dst: str, amount: int, repetitions: int) -> None:
    for _ in range(repetitions):
        with locks[src]:
            time.sleep(0.001)
            with locks[dst]:
                accounts[src] -= amount
                accounts[dst] += amount


t1 = threading.Thread(
    target=transfer,
    args=("A", "B", 10, 100),
    name="кассир-1",
)
t2 = threading.Thread(
    target=transfer,
    args=("B", "A", 10, 100),
    name="кассир-2",
)
t1.start()
t2.start()
t1.join()
t2.join()

faulthandler.cancel_dump_traceback_later()
print("Готово:", accounts, "сумма =", sum(accounts.values()))
