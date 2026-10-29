"""Три варианта задачи обедающих философов со статистикой."""

from __future__ import annotations

import argparse
import threading
import time
from dataclasses import dataclass, field


PHILOSOPHERS = 5


@dataclass
class Statistics:
    eaten: list[int] = field(default_factory=lambda: [0] * PHILOSOPHERS)
    max_wait: list[float] = field(default_factory=lambda: [0.0] * PHILOSOPHERS)
    guard: threading.Lock = field(default_factory=threading.Lock)

    def record(self, philosopher: int, waited: float) -> None:
        with self.guard:
            self.eaten[philosopher] += 1
            self.max_wait[philosopher] = max(self.max_wait[philosopher], waited)


def print_statistics(title: str, stats: Statistics, alive: list[int]) -> None:
    print(f"\n=== {title} ===")
    for philosopher in range(PHILOSOPHERS):
        print(
            f"Философ {philosopher}: поел {stats.eaten[philosopher]:4d} раз; "
            f"максимальное ожидание {stats.max_wait[philosopher]:.4f} с"
        )
    print("Всего приёмов пищи:", sum(stats.eaten))
    print("Зависшие потоки:", alive or "нет")


def run_naive(duration: float) -> None:
    forks = [threading.Lock() for _ in range(PHILOSOPHERS)]
    stats = Statistics()
    left_taken = threading.Barrier(PHILOSOPHERS)
    started = time.perf_counter()

    def philosopher(number: int) -> None:
        left = forks[number]
        right = forks[(number + 1) % PHILOSOPHERS]
        wait_started = time.perf_counter()
        left.acquire()
        left_taken.wait()
        right.acquire()
        stats.record(number, time.perf_counter() - wait_started)

    threads = [
        threading.Thread(target=philosopher, args=(number,), name=f"философ-{number}", daemon=True)
        for number in range(PHILOSOPHERS)
    ]
    for thread in threads:
        thread.start()
    while time.perf_counter() - started < duration:
        time.sleep(min(0.05, duration))
    elapsed = time.perf_counter() - started
    alive = [number for number, thread in enumerate(threads) if thread.is_alive()]
    for number in alive:
        stats.max_wait[number] = max(stats.max_wait[number], elapsed)
    print_statistics("Наивный вариант: взаимоблокировка", stats, alive)


def run_safe(duration: float, strategy: str) -> None:
    forks = [threading.Lock() for _ in range(PHILOSOPHERS)]
    waiter = threading.Semaphore(PHILOSOPHERS - 1) if strategy == "waiter" else None
    stats = Statistics()
    stop = threading.Event()
    start = threading.Barrier(PHILOSOPHERS + 1)

    def take_interruptibly(lock: threading.Lock) -> bool:
        while not stop.is_set():
            if lock.acquire(timeout=0.01):
                return True
        return False

    def philosopher(number: int) -> None:
        left_number = number
        right_number = (number + 1) % PHILOSOPHERS
        start.wait()
        while not stop.is_set():
            wait_started = time.perf_counter()
            if strategy == "ordered":
                first_number, second_number = sorted((left_number, right_number))
                first = forks[first_number]
                second = forks[second_number]
                if not take_interruptibly(first):
                    break
                try:
                    if not take_interruptibly(second):
                        break
                    try:
                        stats.record(number, time.perf_counter() - wait_started)
                        time.sleep(0.001)
                    finally:
                        second.release()
                finally:
                    first.release()
            else:
                assert waiter is not None
                if not waiter.acquire(timeout=0.01):
                    continue
                try:
                    if not take_interruptibly(forks[left_number]):
                        break
                    try:
                        if not take_interruptibly(forks[right_number]):
                            break
                        try:
                            stats.record(number, time.perf_counter() - wait_started)
                            time.sleep(0.001)
                        finally:
                            forks[right_number].release()
                    finally:
                        forks[left_number].release()
                finally:
                    waiter.release()
            time.sleep(0.0005)

    threads = [
        threading.Thread(target=philosopher, args=(number,), name=f"философ-{number}")
        for number in range(PHILOSOPHERS)
    ]
    for thread in threads:
        thread.start()
    start.wait()
    time.sleep(duration)
    stop.set()
    for thread in threads:
        thread.join()
    alive = [number for number, thread in enumerate(threads) if thread.is_alive()]
    title = "Упорядоченный захват вилок" if strategy == "ordered" else "Официант: семафор на 4 места"
    print_statistics(title, stats, alive)


def main() -> None:
    parser = argparse.ArgumentParser(description="Обедающие философы")
    parser.add_argument("--duration", type=float, default=10.0, help="секунд на вариант")
    parser.add_argument(
        "--mode",
        choices=["all", "naive", "ordered", "waiter"],
        default="all",
    )
    args = parser.parse_args()
    if args.duration <= 0:
        parser.error("duration должен быть положительным")

    if args.mode in {"all", "naive"}:
        run_naive(args.duration)
    if args.mode in {"all", "ordered"}:
        run_safe(args.duration, "ordered")
    if args.mode in {"all", "waiter"}:
        run_safe(args.duration, "waiter")


if __name__ == "__main__":
    main()
