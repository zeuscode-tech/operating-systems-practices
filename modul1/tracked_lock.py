"""TrackedLock: блокировка с графом ожидания и обнаружением циклов."""

from __future__ import annotations

import threading
from collections import defaultdict


class DeadlockDetected(RuntimeError):
    """Исключение вместо вечного ожидания при обнаружении цикла."""


class WaitGraph:
    def __init__(self) -> None:
        self._guard = threading.Lock()
        self._edges: dict[str, set[str]] = defaultdict(set)

    def add_wait(self, waiter: str, owner: str) -> list[str] | None:
        with self._guard:
            self._edges[waiter].add(owner)
            self._edges.setdefault(owner, set())
            return self._find_cycle_from(waiter)

    def remove_waiter(self, waiter: str) -> None:
        with self._guard:
            self._edges.pop(waiter, None)

    def _find_cycle_from(self, start: str) -> list[str] | None:
        path: list[str] = []
        position: dict[str, int] = {}

        def visit(node: str) -> list[str] | None:
            position[node] = len(path)
            path.append(node)
            for neighbor in self._edges.get(node, set()):
                if neighbor in position:
                    begin = position[neighbor]
                    return path[begin:] + [neighbor]
                cycle = visit(neighbor)
                if cycle:
                    return cycle
            path.pop()
            position.pop(node, None)
            return None

        return visit(start)


GLOBAL_WAIT_GRAPH = WaitGraph()


class TrackedLock:
    def __init__(self, name: str, graph: WaitGraph = GLOBAL_WAIT_GRAPH) -> None:
        self.name = name
        self._lock = threading.Lock()
        self._state_guard = threading.Lock()
        self._owner: str | None = None
        self._graph = graph

    @property
    def owner(self) -> str | None:
        with self._state_guard:
            return self._owner

    def acquire(self) -> bool:
        thread_name = threading.current_thread().name
        if self._lock.acquire(blocking=False):
            with self._state_guard:
                self._owner = thread_name
            return True

        owner = self.owner
        if owner is None:
            self._lock.acquire()
            with self._state_guard:
                self._owner = thread_name
            return True

        cycle = self._graph.add_wait(thread_name, owner)
        print(f"{thread_name} ждёт {self.name}, владелец {owner}", flush=True)
        if cycle:
            self._graph.remove_waiter(thread_name)
            chain = " -> ".join(cycle)
            raise DeadlockDetected(f"обнаружен цикл ожидания: {chain}")

        try:
            self._lock.acquire()
            with self._state_guard:
                self._owner = thread_name
            return True
        finally:
            self._graph.remove_waiter(thread_name)

    def release(self) -> None:
        thread_name = threading.current_thread().name
        with self._state_guard:
            if self._owner != thread_name:
                raise RuntimeError(
                    f"{thread_name} не может освободить {self.name}; владелец {self._owner}"
                )
            self._owner = None
        self._lock.release()

    def __enter__(self) -> "TrackedLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self.release()
        return False
