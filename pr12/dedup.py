#!/usr/bin/env python3
"""Поиск дубликатов; замена жёсткими ссылками только с --apply."""

from __future__ import annotations

import argparse
import hashlib
import os
from collections import defaultdict
from pathlib import Path


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def groups(root: Path) -> list[list[Path]]:
    by_size: dict[int, list[Path]] = defaultdict(list)
    for path in root.rglob("*"):
        if path.is_file() and not path.is_symlink():
            by_size[path.stat().st_size].append(path)

    result: list[list[Path]] = []
    for candidates in by_size.values():
        if len(candidates) < 2:
            continue
        by_hash: dict[str, list[Path]] = defaultdict(list)
        for path in candidates:
            by_hash[digest(path)].append(path)
        result.extend(group for group in by_hash.values() if len(group) > 1)
    return result


def deduplicate(root: Path, apply: bool) -> tuple[int, int]:
    duplicate_files = 0
    saved = 0
    for group in groups(root):
        original = group[0]
        print(f"Оригинал: {original}")
        for duplicate in group[1:]:
            duplicate_files += 1
            saved += duplicate.stat().st_size
            same_inode = original.stat().st_ino == duplicate.stat().st_ino
            print(f"  дубликат: {duplicate} already-linked={same_inode}")
            if apply and not same_inode:
                temporary = duplicate.with_name(duplicate.name + ".dedup-tmp")
                if temporary.exists():
                    temporary.unlink()
                os.link(original, temporary)
                os.replace(temporary, duplicate)
    return duplicate_files, saved


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--apply", action="store_true", help="заменить дубликаты ссылками")
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error("root должен быть каталогом")
    count, saved = deduplicate(args.root, args.apply)
    mode = "применено" if args.apply else "только анализ"
    print(f"Режим: {mode}")
    print(f"Дубликатов: {count}")
    print(f"Потенциальная экономия: {saved} байт")


if __name__ == "__main__":
    main()
