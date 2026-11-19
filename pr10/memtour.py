#!/usr/bin/env python3
"""Параметры страниц и разложение виртуального адреса процесса."""

import ctypes
import math
import os
import platform


def main() -> None:
    page_size = os.sysconf("SC_PAGE_SIZE")
    buffer = ctypes.create_string_buffer(64)
    address = ctypes.addressof(buffer)
    page, offset = divmod(address, page_size)
    print(f"ОС: {platform.system()} {platform.machine()}")
    print(f"PID: {os.getpid()}")
    print(f"Размер страницы: {page_size} байт")
    print(f"Бит на смещение: {int(math.log2(page_size))}")
    print(f"Виртуальный адрес: {address:#x}")
    print(f"Номер страницы: {page:#x}")
    print(f"Смещение: {offset:#x} = {offset}")


if __name__ == "__main__":
    main()
