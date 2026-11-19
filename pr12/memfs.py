#!/usr/bin/env python3
"""Минимальная FUSE-ФС в памяти для Linux (уровень C)."""

from __future__ import annotations

import argparse
import errno
import os
import stat
import time

from fuse import FUSE, FuseOSError, Operations


class MemoryFS(Operations):
    def __init__(self) -> None:
        now = time.time()
        self.files = {"/": {"st_mode": stat.S_IFDIR | 0o755, "st_nlink": 2, "st_ctime": now, "st_mtime": now, "st_atime": now}}
        self.data: dict[str, bytes] = {}
        self.accesses: dict[str, int] = {}

    def getattr(self, path: str, fh=None):
        if path not in self.files:
            raise FuseOSError(errno.ENOENT)
        result = dict(self.files[path])
        result["st_size"] = len(self.data.get(path, b""))
        return result

    def readdir(self, path: str, fh):
        return [".", "..", *[name[1:] for name in self.files if name != "/" and "/" not in name[1:]]]

    def create(self, path: str, mode: int, fi=None):
        now = time.time()
        self.files[path] = {"st_mode": stat.S_IFREG | mode, "st_nlink": 1, "st_ctime": now, "st_mtime": now, "st_atime": now}
        self.data[path] = b""
        self.accesses[path] = 0
        return 0

    def open(self, path: str, flags: int):
        if path not in self.files:
            raise FuseOSError(errno.ENOENT)
        return 0

    def read(self, path: str, size: int, offset: int, fh):
        self.accesses[path] = self.accesses.get(path, 0) + 1
        return self.data[path][offset : offset + size]

    def write(self, path: str, value: bytes, offset: int, fh):
        current = self.data.get(path, b"")
        current = current.ljust(offset, b"\0")
        self.data[path] = current[:offset] + value + current[offset + len(value) :]
        self.files[path]["st_mtime"] = time.time()
        self.accesses[path] = self.accesses.get(path, 0) + 1
        return len(value)

    def truncate(self, path: str, length: int, fh=None):
        self.data[path] = self.data.get(path, b"")[:length].ljust(length, b"\0")

    def unlink(self, path: str):
        self.files.pop(path, None)
        self.data.pop(path, None)
        self.accesses.pop(path, None)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mountpoint")
    args = parser.parse_args()
    FUSE(MemoryFS(), args.mountpoint, foreground=True)


if __name__ == "__main__":
    main()
