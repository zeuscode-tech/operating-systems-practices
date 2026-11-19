#!/usr/bin/env python3
"""Минимальный HTTP-сервис для экспериментов с контейнерами."""

from __future__ import annotations

import json
import os
import platform
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            payload = {"status": "ok"}
            status = 200
        elif self.path == "/info":
            payload = {
                "pid": os.getpid(),
                "uid": os.getuid() if hasattr(os, "getuid") else None,
                "hostname": platform.node(),
                "python": platform.python_version(),
            }
            status = 200
        else:
            payload = {"error": "not found"}
            status = 404
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        print(f"HTTP {self.address_string()} {format % args}")


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Сервис запущен на порту {port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
