"""Проверка TrackedLock на переводах с обратным порядком блокировок."""

from __future__ import annotations

import threading

from tracked_lock import DeadlockDetected, TrackedLock


accounts = {"A": 1000, "B": 1000}
locks = {"A": TrackedLock("счёт A"), "B": TrackedLock("счёт B")}
first_locks_taken = threading.Barrier(2)
detected: list[str] = []


def transfer_once(src: str, dst: str, amount: int) -> None:
    name = threading.current_thread().name
    try:
        with locks[src]:
            print(f"{name} захватил счёт {src}", flush=True)
            first_locks_taken.wait()
            with locks[dst]:
                accounts[src] -= amount
                accounts[dst] += amount
                print(f"{name} выполнил перевод {src} -> {dst}", flush=True)
    except DeadlockDetected as error:
        detected.append(str(error))
        print(f"{name}: {error}", flush=True)


def main() -> None:
    threads = [
        threading.Thread(target=transfer_once, args=("A", "B", 10), name="кассир-1"),
        threading.Thread(target=transfer_once, args=("B", "A", 10), name="кассир-2"),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    print("Завершены оба потока:", all(not thread.is_alive() for thread in threads))
    print("Обнаружено циклов:", len(detected))
    print("Итоговые счета:", accounts)
    print("Сумма сохранена:", sum(accounts.values()) == 2000)


if __name__ == "__main__":
    main()
