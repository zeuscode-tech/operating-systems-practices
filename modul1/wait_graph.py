"""Построение графа ожидания по waitlog.txt и поиск взаимоблокировок."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path


Graph = dict[str, set[str]]


def read_events(path: Path) -> list[tuple[int, str, str, str]]:
    events: list[tuple[int, str, str, str]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        moment, process, action, resource = line.split()
        if action not in {"acquire", "wait", "release"}:
            raise ValueError(f"Неизвестное событие {action!r}")
        events.append((int(moment), process, action, resource))
    return events


def replay(events: list[tuple[int, str, str, str]]) -> tuple[dict[str, str], dict[str, str]]:
    owners: dict[str, str] = {}
    waiting: dict[str, str] = {}

    for moment, process, action, resource in events:
        if action == "acquire":
            owner = owners.get(resource)
            if owner is not None and owner != process:
                raise ValueError(f"t={moment}: {resource} уже принадлежит {owner}")
            owners[resource] = process
            waiting.pop(process, None)
        elif action == "wait":
            if resource not in owners:
                raise ValueError(f"t={moment}: {process} ждёт свободный ресурс {resource}")
            waiting[process] = resource
        elif action == "release":
            if owners.get(resource) != process:
                raise ValueError(f"t={moment}: {process} не владеет {resource}")
            del owners[resource]

    return owners, waiting


def build_graph(owners: dict[str, str], waiting: dict[str, str]) -> Graph:
    graph: dict[str, set[str]] = defaultdict(set)
    for process, resource in waiting.items():
        owner = owners.get(resource)
        if owner is not None and owner != process:
            graph[process].add(owner)
            graph.setdefault(owner, set())
    return dict(graph)


def strongly_connected_components(graph: Graph) -> list[list[str]]:
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    components: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlink[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for neighbor in graph.get(node, set()):
            if neighbor not in indices:
                visit(neighbor)
                lowlink[node] = min(lowlink[node], lowlink[neighbor])
            elif neighbor in on_stack:
                lowlink[node] = min(lowlink[node], indices[neighbor])

        if lowlink[node] == indices[node]:
            component: list[str] = []
            while True:
                current = stack.pop()
                on_stack.remove(current)
                component.append(current)
                if current == node:
                    break
            components.append(sorted(component))

    nodes = set(graph)
    for targets in graph.values():
        nodes.update(targets)
    for node in sorted(nodes):
        if node not in indices:
            visit(node)
    return components


def cycle_components(graph: Graph) -> list[list[str]]:
    cycles: list[list[str]] = []
    for component in strongly_connected_components(graph):
        if len(component) > 1:
            cycles.append(component)
        elif component and component[0] in graph.get(component[0], set()):
            cycles.append(component)
    return cycles


def reaches_any(graph: Graph, start: str, targets: set[str]) -> bool:
    stack = [start]
    visited: set[str] = set()
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        if node in targets:
            return True
        stack.extend(graph.get(node, set()))
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Детектор взаимоблокировок по журналу")
    parser.add_argument("waitlog", type=Path)
    args = parser.parse_args()

    events = read_events(args.waitlog)
    owners, waiting = replay(events)
    graph = build_graph(owners, waiting)
    cycles = cycle_components(graph)
    cycle_nodes = {node for component in cycles for node in component}
    dependent = sorted(
        process
        for process in waiting
        if process not in cycle_nodes and reaches_any(graph, process, cycle_nodes)
    )
    other_waiting = sorted(set(waiting) - cycle_nodes - set(dependent))

    print("Владельцы ресурсов на конец журнала:")
    for resource, process in sorted(owners.items()):
        print(f"  {resource}: {process}")
    print("Ожидающие процессы:")
    for process, resource in sorted(waiting.items()):
        print(f"  {process} ждёт {resource}")
    print("Граф ожидания:")
    for process in sorted(graph):
        for owner in sorted(graph[process]):
            print(f"  {process} -> {owner}")

    if cycles:
        print("Цикл обнаружен: True")
        for number, component in enumerate(cycles, start=1):
            print(f"  Цикл {number}, участники:", ", ".join(component))
    else:
        print("Цикл обнаружен: False")
    print("Заблокированы циклом, но не входят в него:", ", ".join(dependent) or "нет")
    print("Ждут процесс, который сам не заблокирован:", ", ".join(other_waiting) or "нет")


if __name__ == "__main__":
    main()
