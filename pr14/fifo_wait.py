#!/usr/bin/env python3
"""Busy waiting против блокирующего ожидания данных в pipe."""

from __future__ import annotations

import os
import selectors
import threading
import time


DELAY = 0.25


def delayed_write(fd: int) -> None:
    time.sleep(DELAY)
    os.write(fd, b"ready")
    os.close(fd)


def experiment(blocking: bool) -> tuple[float, float, int]:
    read_fd, write_fd = os.pipe()
    os.set_blocking(read_fd, blocking)
    producer = threading.Thread(target=delayed_write, args=(write_fd,))
    producer.start()
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    checks = 0
    if blocking:
        selector = selectors.DefaultSelector()
        selector.register(read_fd, selectors.EVENT_READ)
        selector.select()
        data = os.read(read_fd, 5)
        selector.close()
        checks = 1
    else:
        while True:
            checks += 1
            try:
                data = os.read(read_fd, 5)
                if data:
                    break
            except BlockingIOError:
                pass
    cpu = time.process_time() - cpu_start
    wall = time.perf_counter() - wall_start
    os.close(read_fd)
    producer.join()
    return wall, cpu, checks


def main() -> None:
    busy = experiment(False)
    blocked = experiment(True)
    print("режим          wall, с   CPU, с   проверок")
    print(f"busy waiting   {busy[0]:7.4f}  {busy[1]:7.4f}  {busy[2]:>9}")
    print(f"blocking       {blocked[0]:7.4f}  {blocked[1]:7.4f}  {blocked[2]:>9}")
    print("Вывод: блокирующее ожидание освобождает процессор до готовности данных.")


if __name__ == "__main__":
    main()
