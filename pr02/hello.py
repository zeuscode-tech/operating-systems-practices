#!/usr/bin/env python3

from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent / "data" / "01.log"


with DATA_FILE.open("rb") as file:
    content = file.read()

print(len(content))
